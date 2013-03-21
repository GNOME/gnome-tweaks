import os.path
import zipfile
import tempfile
import logging
import json

from gi.repository import Gtk
from gi.repository import GLib

from operator import itemgetter
from gtweak.utils import extract_zip_file, execute_subprocess
from gtweak.gshellwrapper import GnomeShell, GnomeShellFactory
from gtweak.tweakmodel import Tweak, TweakGroup
from gtweak.widgets import FileChooserButton, build_label_beside_widget, build_horizontal_sizegroup, build_tight_button, UI_BOX_SPACING

def N_(x): return x

class _ShellExtensionTweak(Tweak):

    def __init__(self, shell, ext, **options):
        Tweak.__init__(self, ext["name"], ext.get("description",""), **options)

        self._shell = shell
        state = ext.get("state")
        uuid = ext["uuid"]

        sw = Gtk.Switch()
        sw.set_active(self._shell.extension_is_active(state, uuid))
        sw.connect('notify::active', self._on_extension_toggled, uuid)

        info = None
        warning = None
        sensitive = False
        if state == GnomeShell.EXTENSION_STATE["ENABLED"] or \
           state == GnomeShell.EXTENSION_STATE["DISABLED"] or \
           state == GnomeShell.EXTENSION_STATE["INITIALIZED"]:
            sensitive = True
        elif state == GnomeShell.EXTENSION_STATE["DOWNLOADING"]:
            info = _("Extension downloading")
        elif state == GnomeShell.EXTENSION_STATE["ERROR"]:
            warning = _("Error loading extension")
        elif state == GnomeShell.EXTENSION_STATE["OUT_OF_DATE"]:
            warning = _("Extension does not support shell version")
        else:
            warning = _("Unknown extension error")
            logging.critical(warning)
        sw.set_sensitive(sensitive)

        widgets = []
        if self._shell.SUPPORTS_EXTENSION_PREFS:
            prefs = os.path.join(self._shell.EXTENSION_DIR, uuid, "prefs.js")
            if os.path.exists(prefs):
                cfg = build_tight_button(Gtk.STOCK_PREFERENCES)
                cfg.connect("clicked", self._on_configure_clicked, uuid)
                widgets.append(cfg)

        if ext.get("type") == GnomeShell.EXTENSION_TYPE["PER_USER"]:
            deleteButton = build_tight_button(Gtk.STOCK_DELETE)
            deleteButton.connect("clicked", self._on_extension_delete, uuid, ext["name"])
            widgets.append(deleteButton)

        widgets.append(sw)

        self.widget = build_label_beside_widget(
                        ext["name"].lower().capitalize(),
                        *widgets,
                        warning=warning)
        self.widget_for_size_group = None

    def _on_configure_clicked(self, btn, uuid):
        execute_subprocess(['gnome-shell-extension-prefs', uuid], block=False)

    def _on_extension_toggled(self, sw, active, uuid):
        if not sw.get_active():
            self._shell.disable_extension(uuid)
        else:
            self._shell.enable_extension(uuid)

        if self._shell.EXTENSION_NEED_RESTART:
            self.notify_action_required(
                _("The shell must be restarted for changes to take effect"),
                _("Restart"),
                self._shell.restart)

    def _on_extension_delete(self, btn, uuid, name):
        path = os.path.join(self._shell.EXTENSION_DIR, uuid)
        if os.path.exists(path):
            first_message = _("Delete an extension")        
            second_message = _("Do you want to delete the extension ")+name+"?"
            dialog = Gtk.MessageDialog(None,0,type=Gtk.MessageType.QUESTION,
                                   buttons=Gtk.ButtonsType.YES_NO,
                                   message_format=first_message)
            dialog.format_secondary_text(second_message)
            response = dialog.run()
            if response == Gtk.ResponseType.YES:
                self._shell.uninstall_extension(uuid)
            dialog.destroy()

class _ShellExtensionInstallerTweak(Tweak):

    def __init__(self, shell, **options):
        Tweak.__init__(self, _("Install Shell Extension"), "", **options)

        self._shell = shell

        chooser = FileChooserButton(
                        _("Select an extension"),
                        True,
                        "application/zip")
        chooser.connect("file-set", self._on_file_set)

        hb = Gtk.HBox(spacing=UI_BOX_SPACING)
        hb.pack_start(
                Gtk.LinkButton.new_with_label("https://extensions.gnome.org",_("Get more extensions")),
                False, False, 0)
        hb.pack_start(chooser, False, False, 0)

        self.widget = build_label_beside_widget(self.name, hb)
        self.widget_for_size_group = hb

    def _on_file_set(self, chooser):
        f = chooser.get_filename()

        with zipfile.ZipFile(f, 'r') as z:
            try:
                fragment = ()
                file_extension = None
                file_metadata = None
                for n in z.namelist():
                    if n.endswith("metadata.json"):
                        fragment = n.split("/")[0:-1]
                        file_metadata = n
                    if n.endswith("extension.js"):
                        if file_extension:
                            raise Exception("Only one extension per zip file")
                        file_extension = n

                if not file_metadata:
                    raise Exception("Could not find metadata.json")
                if not file_extension:
                    raise Exception("Could not find extension.js")

                #extract the extension uuid
                extension_uuid = None
                tmp = tempfile.mkdtemp()
                z.extract(file_metadata, tmp)
                with open(os.path.join(tmp, file_metadata)) as f:
                    try:
                        extension_uuid = json.load(f)["uuid"]
                    except:
                        logging.warning("Invalid extension format", exc_info=True)

                ok = False
                if extension_uuid:
                    ok, updated = extract_zip_file(
                                    z,
                                    "/".join(fragment),
                                    os.path.join(self._shell.EXTENSION_DIR, extension_uuid))

                if ok:
                    if updated:
                        verb = _("%s extension updated successfully") % extension_uuid
                    else:
                        verb = _("%s extension installed successfully") % extension_uuid

                    self.notify_action_required(
                        verb,
                        _("Restart"),
                        self._shell.restart)

                else:
                    self.notify_error(_("Error installing extension"))


            except:
                #does not look like a valid theme
                self.notify_error(_("Invalid extension"))
                logging.warning("Error parsing theme zip", exc_info=True)

        #set button back to default state
        chooser.unselect_all()

class ShellExtensionTweakGroup(TweakGroup):
    def __init__(self):
        TweakGroup.__init__(self, N_("Shell Extensions"))

        extension_tweaks = []
        sg = build_horizontal_sizegroup()

        #check the shell is running
        try:
            shell = GnomeShellFactory().get_shell()

            #add the extension installer
            extension_tweaks.append(
                _ShellExtensionInstallerTweak(shell, size_group=sg))

            try:
                #add a tweak for each installed extension
                extensions = sorted(shell.list_extensions().values(), key=itemgetter("name"))
                for extension in extensions:
                    try:
                        extension_tweaks.append(
                            _ShellExtensionTweak(shell, extension, size_group=sg))
                    except:
                        logging.warning("Invalid extension", exc_info=True)
            except:
                logging.warning("Error listing extensions", exc_info=True)
        except:
            logging.warning("Error detecting shell", exc_info=True)

        self.set_tweaks(*extension_tweaks)

TWEAK_GROUPS = (
        ShellExtensionTweakGroup(),
)
