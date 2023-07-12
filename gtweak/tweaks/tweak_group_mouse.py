# Copyright (c) 2011 John Stowers
# SPDX-License-Identifier: GPL-3.0+
# License-Filename: LICENSES/GPL-3.0


from gi.repository import Gio, Gtk

from gtweak.gshellwrapper import GnomeShellFactory
from gtweak.widgets import (ListBoxTweakGroup, GSettingsSwitchTweak, GSettingsSwitchTweakValue,
                            Title, Tweak, build_listrow_hbox)

_shell = GnomeShellFactory().get_shell()
_shell_loaded = _shell is not None


class KeyThemeSwitcher(GSettingsSwitchTweakValue):
    def __init__(self, **options):
        GSettingsSwitchTweakValue.__init__(self,
                                           _("Emacs Input"),
                                           "org.gnome.desktop.interface",
                                           "gtk-key-theme",
                                           desc=_("Overrides shortcuts to use keybindings from the Emacs editor."),
                                           **options)

    def get_active(self):
        return "Emacs" in self.settings.get_string(self.key_name)

    def set_active(self, v):
        if v:
            self.settings.set_string(self.key_name, "Emacs")
        else:
            self.settings.set_string(self.key_name, "Default")

class ClickMethod(Gtk.ListBox, Tweak):

    def __init__(self, **options):
        Gtk.ListBox.__init__(self)
        Tweak.__init__(self, _("Mouse Click Emulation"), _("Mouse Click Emulation"))
        self.add_css_class("boxed-list")

        self.settings = Gio.Settings("org.gnome.desktop.peripherals.touchpad")
        self.key_name = "click-method"

        self.set_selection_mode(Gtk.SelectionMode.NONE)

        row = Gtk.ListBoxRow()
        desc = _("Click the touchpad with two fingers for right-click and three fingers for middle-click.")
        hbox = build_listrow_hbox(_("Fingers"), desc)
        self.check_fingers = self._create_check_mark("fingers")
        hbox.append(self.check_fingers)
        row.set_child(hbox)
        self.append(row)

        row = Gtk.ListBoxRow()
        desc = _("Click the bottom right of the touchpad for right-click and the bottom middle for middle-click.")
        hbox = build_listrow_hbox(_("Area"), desc)
        self.check_area = self._create_check_mark("areas")
        hbox.append(self.check_area)
        row.set_child(hbox)
        self.append(row)

        row = Gtk.ListBoxRow()
        desc = _("Don’t use mouse click emulation.")
        hbox = build_listrow_hbox(_("Disabled"), desc)
        self.check_disabled = self._create_check_mark("none")
        hbox.append(self.check_disabled)
        row.set_child(hbox)
        self.append(row)

        self.connect('row-activated', self.on_row_clicked)

    def on_row_clicked(self, box, row):
        if row.get_index() == 0:
            self.settings[self.key_name] = "fingers"
            self.check_fingers.show()
            self.check_area.hide()
            self.check_disabled.hide()
        elif row.get_index() == 1:
            self.settings[self.key_name] = "areas"
            self.check_fingers.hide()
            self.check_area.show()
            self.check_disabled.hide()
        else:
            self.settings[self.key_name] = "none"
            self.check_fingers.hide()
            self.check_area.hide()
            self.check_disabled.show()

    def _create_check_mark(self, key_name: str) -> Gtk.Image:
        """ Creates an Image check mark with the associated setting

        :param key_name: The setting option to trigger when visible
        :return: Gtk.Image
        """
        check_mark = Gtk.Image.new_from_icon_name("object-select-symbolic")
        check_mark.set_visible(self.settings[self.key_name] == key_name)
        return check_mark


TWEAK_GROUP = ListBoxTweakGroup("mouse", _("Mouse"),
    Title(_("Mouse"), ""),
    GSettingsSwitchTweak(_("Middle Click Paste"),
                         "org.gnome.desktop.interface",
                         "gtk-enable-primary-paste"),
    Title(_("Touchpad"), ""),
    GSettingsSwitchTweak(_("Disable While Typing"),
                         "org.gnome.desktop.peripherals.touchpad",
                         "disable-while-typing",
                         schema_filename="org.gnome.desktop.peripherals.gschema.xml"),
    Title(_("Mouse Click Emulation"), _("Mouse Click Emulation"), top=True),
    ClickMethod(),
)
