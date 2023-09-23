# Copyright (c) 2011 John Stowers
# SPDX-License-Identifier: GPL-3.0+
# License-Filename: LICENSES/GPL-3.0


from gi.repository import Adw, Gio

from gtweak.gshellwrapper import GnomeShellFactory
from gtweak.widgets import (ListBoxTweakGroup, GSettingsSwitchTweak, GSettingsSwitchTweakValue,
                            Title, Tweak, TickActionRow)

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

class ClickMethod(Adw.PreferencesGroup, Tweak):

    def __init__(self, **options):
        name: str = _("Mouse Click Emulation")
        desc: str = _("Mouse Click Emulation")
        Adw.PreferencesGroup.__init__(self)
        Tweak.__init__(self, name, desc, **options)
        self.set_title(name)
        self.add_css_class("boxed-list")

        self.settings = Gio.Settings("org.gnome.desktop.peripherals.touchpad")
        self.key_name = "click-method"

        self.row_fingers = self._setup_action_row(
            key_name="fingers", title=_("Fingers"),
            subtitle=_(
                "Click the touchpad with two fingers for right-click and three fingers for middle-click."))

        self.row_area = self._setup_action_row(
            key_name="areas", title=_("Area"),
            subtitle=_(
                "Click the bottom right of the touchpad for right-click and the bottom middle for middle-click."))

        self.row_disabled= self._setup_action_row(
            key_name="none", title=_("Disabled"),
            subtitle=_(
                "Don’t use mouse click emulation."))

        self.settings.connect("changed", self._on_settings_changed)

    def _setup_action_row(self, key_name: str, title: str, subtitle: str) -> TickActionRow:

        action_row = TickActionRow(title, subtitle, key_name)
        action_row.img.set_visible(self.settings[self.key_name] == key_name)
        action_row.connect("activated", self._on_row_clicked)

        self.add(action_row)
        return action_row

    def _on_settings_changed(self, settings, key: str):
        keyvalue = settings[key]
        if keyvalue == "fingers":
            self.row_fingers.img.show()
            self.row_area.img.hide()
            self.row_disabled.img.hide()
        elif keyvalue == "areas":
            self.row_fingers.img.hide()
            self.row_area.img.show()
            self.row_disabled.img.hide()
        else:  # none
            self.row_fingers.img.hide()
            self.row_area.img.hide()
            self.row_disabled.img.show()

    def _on_row_clicked(self, row: TickActionRow):
        self.settings[self.key_name] = row.keyvalue

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
