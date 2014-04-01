import os.path
import zipfile
import tempfile
import logging
import json

from gi.repository import Gtk
from gi.repository import GLib
from gi.repository import Pango

from operator import itemgetter
from gtweak.utils import extract_zip_file, execute_subprocess
from gtweak.gshellwrapper import GnomeShell, GnomeShellFactory
from gtweak.tweakmodel import Tweak
from gtweak.widgets import FileChooserButton, build_label_beside_widget, build_horizontal_sizegroup, build_tight_button, UI_BOX_SPACING, ListBoxTweakGroup
from gtweak.egowrapper import ExtensionsDotGnomeDotOrg
from gtweak.utils import DisableExtension

def N_(x): return x

def _fix_shell_version_for_ego(version):
    #extensions.gnome.org uses a weird versioning system,
    #3.10.0 is 3.10, 3.10.0.x (x is ignored)
    #drop the pico? release
    version = '.'.join(version.split('.')[0:3])
    if version[-1] == '0':
        #if it is .0, drop that too
        return '.'.join(version.split('.')[0:2])
    else:
        return version

class _ShellExtensionTweak(Gtk.ListBoxRow, Tweak):

    def __init__(self, shell, ext, **options):
        Gtk.ListBoxRow.__init__(self)
        Tweak.__init__(self, ext["name"], ext.get("description",""), **options)

        self.hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.hbox.props.border_width = 10
        self.hbox.props.spacing = UI_BOX_SPACING
    
        self._shell = shell
        state = ext.get("state")
        uuid = ext["uuid"]

        sw = Gtk.Switch()
        sw.props.vexpand = False
        sw.props.valign = Gtk.Align.CENTER
        sw.set_active(self._shell.extension_is_active(state, uuid))
        sw.connect('notify::active', self._on_extension_toggled, uuid)
        self.hbox.pack_start(sw, False, False, 0)
                        
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        lbl_name = Gtk.Label(xalign=0.0)
        lbl_name.set_markup("<span size='medium'><b>"+ext["name"].lower().capitalize()+"</b></span>")
        lbl_desc = Gtk.Label(xalign=0.0)
        desc = ext["description"].lower().capitalize().split('\n')[0]
        lbl_desc.set_markup("<span foreground='#A19C9C' size='small'>"+desc+"</span>")
        lbl_desc.props.ellipsize = Pango.EllipsizeMode.END 
        
        vbox.pack_start(lbl_name, False, False, 0)
        vbox.pack_start(lbl_desc, False, False, 0)
        
        self.hbox.pack_start(vbox, True, True, 10)

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


        if info:
            inf = self.make_image("dialog-information-symbolic", info)
            self.hbox.pack_start(inf, False, False, 0)

        if warning:
            wg = self.make_image("dialog-warning-symbolic", warning)
            self.hbox.pack_start(wg, False, False, 0)

        if self._shell.SUPPORTS_EXTENSION_PREFS:
            prefs = os.path.join(ext['path'], "prefs.js")
            if os.path.exists(prefs):
                icon = Gtk.Image()  
                icon.set_from_icon_name("emblem-system-symbolic", Gtk.IconSize.BUTTON)
                btn = Gtk.Button()
                btn.props.vexpand = False
                btn.props.valign = Gtk.Align.CENTER
                btn.add(icon)
                btn.connect("clicked", self._on_configure_clicked, uuid)
                self.hbox.pack_start(btn, False, False, 0)

        btn = Gtk.Button(_("Remove"))
        btn.props.vexpand = False
        btn.props.valign = Gtk.Align.CENTER
        btn.set_sensitive(False)
        self.hbox.pack_start(btn, False, False, 0)
        if ext.get("type") == GnomeShell.EXTENSION_TYPE["PER_USER"]:
            btn.get_style_context().add_class("suggested-action")
            btn.set_sensitive(True)
            btn.connect("clicked", self._on_extension_delete, uuid, ext["name"])
        self.deleteButton = btn

        de = DisableExtension()
        de.connect('disable-extension', self._on_disable_extension, sw)
    
        self.add(self.hbox)
        self.widget_for_size_group = None

    def _on_disable_extension(self, de, sw):
        sw.set_active(False)

    def _on_configure_clicked(self, btn, uuid):
        execute_subprocess(['gnome-shell-extension-prefs', uuid], block=False)

    def _on_extension_toggled(self, sw, active, uuid):
        if not sw.get_active():
            self._shell.disable_extension(uuid)
        else:
            self._shell.enable_extension(uuid)

    def _on_extension_delete(self, btn, uuid, name):
        path = os.path.join(self._shell.EXTENSION_DIR, uuid)
        if os.path.exists(path):
            first_message = _("Uninstall Extension")
            second_message = _("Do you want to uninstall the '%s' extension?") % name
            dialog = Gtk.MessageDialog(
                                   self.main_window,0,
                                   type=Gtk.MessageType.QUESTION,
                                   buttons=Gtk.ButtonsType.YES_NO,
                                   message_format=first_message)
            dialog.format_secondary_text(second_message)
            response = dialog.run()
            if response == Gtk.ResponseType.YES:
                self._shell.uninstall_extension(uuid)
                self.set_sensitive(False)
                btn.get_style_context().remove_class("suggested-action")
            dialog.destroy()

    def _on_extension_update(self, btn, uuid):
        self._shell.uninstall_extension(uuid)
        btn.get_style_context().remove_class("suggested-action")
        btn.set_label(_("Updating"))
        self.set_sensitive(False)
        self._shell.install_remote_extension(uuid,self.reply_handler, self.error_handler, btn)
    
    def reply_handler(self, proxy_object, result, user_data):
        if result == 's':
            self.deleteButton.show()
            user_data.hide()
            self.set_sensitive(True) 

    def error_handler(self, proxy_object, result, user_data):
        user_data.set_label(_("Error"))
        print result

    def add_update_button(self, uuid):
        self.deleteButton.hide()
        updateButton = Gtk.Button(_("Update"))   
        updateButton.get_style_context().add_class("suggested-action")
        updateButton.connect("clicked", self._on_extension_update, uuid)
        updateButton.show()
        self.hbox.pack_end(updateButton, False, False, 0)

    def make_image(self, icon, tip):
        image = Gtk.Image.new_from_icon_name(icon, Gtk.IconSize.MENU)
        image.set_tooltip_text(tip)
        return image    

class _ShellExtensionInstallerTweak(Gtk.Box, Tweak):

    def __init__(self, shell, **options):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.HORIZONTAL)
        Tweak.__init__(self, _("Install Shell Extension"), "", **options)

        self._shell = shell

        chooser = FileChooserButton(
                        _("Select an extension"),
                        True,
                        ["application/zip"])
        chooser.connect("file-set", self._on_file_set)

        hb = Gtk.HBox(spacing=UI_BOX_SPACING)
        hb.pack_start(
                Gtk.LinkButton.new_with_label("https://extensions.gnome.org",_("Get more extensions")),
                False, False, 0)
        hb.pack_start(chooser, False, False, 0)

        build_label_beside_widget(self.name, hb, hbox=self)
        self.widget_for_size_group = hb

        self.loaded = self._shell is not None

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
                    self.notify_information(_("Error installing extension"))


            except:
                #does not look like a valid theme
                self.notify_information(_("Invalid extension"))
                logging.warning("Error parsing theme zip", exc_info=True)

        #set button back to default state
        chooser.unselect_all()

class ShellExtensionTweakGroup(ListBoxTweakGroup):
    def __init__(self):
        extension_tweaks = []
        sg = build_horizontal_sizegroup()

        #check the shell is running
        try:
            shell = GnomeShellFactory().get_shell()
            if shell is None:
                raise Exception("Shell not running or DBus service not available")

            version =  tuple(shell.version.split("."))
            ego = ExtensionsDotGnomeDotOrg(version)
            try:
                #add a tweak for each installed extension
                extensions = sorted(shell.list_extensions().values(), key=itemgetter("name"))
                for extension in extensions:
                    try:
                        extension_widget = _ShellExtensionTweak(shell, extension, size_group=sg)
                        extension_tweaks.append(extension_widget)
                        if extension.get("type") == GnomeShell.EXTENSION_TYPE["PER_USER"]:
                            ego.connect("got-extension-info", self._got_info, extension, extension_widget)
                            ego.query_extension_info(extension["uuid"])
                    except:
                        logging.warning("Invalid extension", exc_info=True)
            except:
                logging.warning("Error listing extensions", exc_info=True)
        except:
            logging.warning("Error detecting shell", exc_info=True)
        
        #add the extension installer
        extension_tweaks.append(
                _ShellExtensionInstallerTweak(shell, size_group=sg))
            
        ListBoxTweakGroup.__init__(self,
                                   _("Extensions"),
                                   *extension_tweaks)
        
        self.set_header_func(self._list_header_func, None)

    def _got_info(self, ego, resp, uuid, extension, widget):
        if uuid == extension["uuid"]:
            resp = resp['shell_version_map']
            shell = GnomeShellFactory().get_shell()
            version = _fix_shell_version_for_ego(shell.version)
            try:
                resp = resp[version]
                if int(resp["version"]) > extension["version"]:
                    widget.add_update_button(uuid)

            except KeyError:
                logging.info("e.g.o no updates for %s (shell version %s extension version %s)" % (
                             uuid,version,extension["version"]))

    def _list_header_func(self, row, before, user_data):
        if before and not row.get_header():
            row.set_header (Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL))

TWEAK_GROUPS = [
        ShellExtensionTweakGroup(),
]
