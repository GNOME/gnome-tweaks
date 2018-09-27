# SPDX-License-Identifier: GPL-3.0+
# License-Filename: LICENSES/GPL-3.0

import os.path
import zipfile
import tempfile
import logging
import json

from gi.repository import Gtk
from gi.repository import GLib
from gi.repository import Gio
from gi.repository import Pango

from operator import itemgetter
from gtweak.utils import extract_zip_file, execute_subprocess
from gtweak.gshellwrapper import GnomeShell, GnomeShellFactory
from gtweak.tweakmodel import Tweak
from gtweak.widgets import FileChooserButton, build_label_beside_widget, build_horizontal_sizegroup, build_tight_button, ListBoxTweakGroup
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
        return _get_shell_major_minor_version(version)
    else:
        return version

def _get_shell_major_minor_version(version):
    return '.'.join(version.split('.')[0:2])

class _ExtensionsBlankState(Gtk.Box, Tweak):

    def __init__(self):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL, spacing=18,
                               valign=Gtk.Align.CENTER)
        Tweak.__init__(self, 'extensions', '')

        self.add(Gtk.Image(icon_name="org.gnome.tweaks-symbolic",
                 pixel_size=128, opacity=0.3))

        self.add(Gtk.Label(label="<b>" + _("No Extensions Installed") + "</b>",
                 use_markup=True, opacity=0.3))

        try:
            self._swInfo = Gio.DesktopAppInfo.new("org.gnome.Software.desktop")

            if self._swInfo:
                btn = Gtk.Button(label=_("Browse in Software"),
                                 always_show_image=True, halign=Gtk.Align.CENTER,
                                 image=Gtk.Image(icon_name="org.gnome.Software-symbolic"))
                btn.connect("clicked", self._on_browse_clicked)
                self.add(btn)

        except:
            logging.warning("Error detecting shell", exc_info=True)

        self.show_all()

    def _on_browse_clicked(self, btn):
        self._swInfo.launch([], None)

class _ExtensionDescriptionLabel(Gtk.Label):

    def do_get_preferred_height_for_width(self, width):
        # Hack: Request the maximum height allowed by the line limit
        if self.get_lines() > 0:
            return Gtk.Label.do_get_preferred_height_for_width(self, 0)
        return Gtk.Label.do_get_preferred_height_for_width(self, width)

class _ShellExtensionTweak(Gtk.ListBoxRow, Tweak):

    def __init__(self, shell, ext, **options):
        Gtk.ListBoxRow.__init__(self)
        Tweak.__init__(self, ext["name"], ext.get("description",""), **options)

        self.hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.hbox.props.border_width = 10
        self.hbox.props.spacing = 12

        self._shell = shell
        state = ext.get("state")
        uuid = ext["uuid"]
        self._app_id = "user/*/extensions-web/shell-extension/" + uuid.replace('@', '_') + "/*"

        shell._settings.bind("disable-user-extensions", self,
                             "sensitive", Gio.SettingsBindFlags.INVERT_BOOLEAN)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        lbl_name = Gtk.Label(xalign=0.0)
        name_markup = GLib.markup_escape_text(ext["name"].lower().capitalize())
        lbl_name.set_markup("<span size='medium'><b>"+name_markup+"</b></span>")
        lbl_desc = _ExtensionDescriptionLabel(xalign=0.0, yalign=0.0, wrap=True, lines=2)
        desc = GLib.markup_escape_text(ext["description"].lower().capitalize().split('\n')[0])
        lbl_desc.set_markup("<span size='small'>"+desc+"</span>")
        lbl_desc.get_style_context().add_class("dim-label")
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


        if info:
            inf = self.make_image("dialog-information-symbolic", info)
            self.hbox.pack_start(inf, False, False, 0)

        if warning:
            wg = self.make_image("dialog-warning-symbolic", warning)
            self.hbox.pack_start(wg, False, False, 0)

        if self._shell.SUPPORTS_EXTENSION_PREFS:
            prefs = os.path.join(ext['path'], "prefs.js")
            if os.path.exists(prefs):
                btn = Gtk.Button.new_from_icon_name("emblem-system-symbolic", Gtk.IconSize.BUTTON)
                btn.props.valign = Gtk.Align.CENTER
                btn.connect("clicked", self._on_configure_clicked, uuid)
                self.hbox.pack_start(btn, False, False, 0)

        sw = Gtk.Switch(sensitive=sensitive)
        sw.props.vexpand = False
        sw.props.valign = Gtk.Align.CENTER
        sw.set_active(self._shell.extension_is_active(state, uuid))
        sw.connect('notify::active', self._on_extension_toggled, uuid)
        self.hbox.pack_start(sw, False, False, 0)

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

    def _on_extension_update(self, btn, uuid):
        self._shell.uninstall_extension(uuid)
        btn.get_style_context().remove_class("suggested-action")
        btn.set_label(_("Updating"))
        self.set_sensitive(False)
        self._shell.install_remote_extension(uuid,self.reply_handler, self.error_handler, btn)

    def do_activate(self):
        bus = Gio.bus_get_sync(Gio.BusType.SESSION, None)
        bus.call('org.gnome.Software',
                 '/org/gnome/Software',
                 'org.freedesktop.Application',
                 'ActivateAction',
                 GLib.Variant('(sava{sv})',
                              ('details', [GLib.Variant('(ss)', (self._app_id, ''))], {})),
                 None, 0, -1, None)

    def reply_handler(self, proxy_object, result, user_data):
        if result == 's':
            user_data.hide()
            self.set_sensitive(True)

    def error_handler(self, proxy_object, result, user_data):
        user_data.set_label(_("Error"))
        print(result)

    def add_update_button(self, uuid):
        updateButton = Gtk.Button(_("Update"))
        updateButton.get_style_context().add_class("suggested-action")
        updateButton.connect("clicked", self._on_extension_update, uuid)
        updateButton.show()
        self.hbox.pack_end(updateButton, False, False, 0)

    def make_image(self, icon, tip):
        image = Gtk.Image.new_from_icon_name(icon, Gtk.IconSize.MENU)
        image.set_tooltip_text(tip)
        return image

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
                extensions = sorted(list(shell.list_extensions().values()), key=itemgetter("name"))
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

        ListBoxTweakGroup.__init__(self,
                                   _("Extensions"),
                                   *extension_tweaks,
                                   activatable=True)

        if shell is None:
            return # we're done

        self.props.valign = Gtk.Align.FILL

        self.titlebar_widget = Gtk.Switch(visible=True)
        shell._settings.bind("disable-user-extensions", self.titlebar_widget,
                             "active", Gio.SettingsBindFlags.INVERT_BOOLEAN)

        self.set_header_func(self._list_header_func, None)
        self.connect("row-activated", self._on_row_activated, None);

        if not len(extension_tweaks):
            placeholder = _ExtensionsBlankState()
            self.set_placeholder(placeholder)
            self.tweaks.append(placeholder)

    def _got_info(self, ego, resp, uuid, extension, widget):
        if uuid == extension["uuid"]:
            resp = resp['shell_version_map']
            shell = GnomeShellFactory().get_shell()
            version = _fix_shell_version_for_ego(shell.version)

            if version in resp:
                resp = resp[version]
                ext_version = extension["version"] if "version" in extension else 0
                if int(resp["version"]) > ext_version:
                    widget.add_update_button(uuid)
            else:
                ext_version = extension["version"] if "version" in extension else "unknown"
                logging.info("e.g.o no updates for %s (shell version %s extension version %s)" % (
                             uuid, version, ext_version))

    def _list_header_func(self, row, before, user_data):
        if before and not row.get_header():
            row.set_header (Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL))

    def _on_row_activated(self, list, row, user_data):
        row.activate()

TWEAK_GROUPS = [
        ShellExtensionTweakGroup(),
]
