# Copyright (c) 2011 John Stowers
# SPDX-License-Identifier: GPL-3.0+
# License-Filename: LICENSES/GPL-3.0


from gi.repository import Adw, Gio, Gtk

from gtweak.widgets import (CheckPreferencesRow, ListBoxTweakGroup, GSettingsSwitchTweak, GSettingsSwitchTweakValue, ListBoxTweakSubgroup,
                           Tweak)


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

class ClickMethod(Adw.PreferencesRow, Tweak):

    def __init__(self, **options):
        title = _("Mouse Click Emulation")

        Adw.PreferencesRow.__init__(self, title=title, activatable=False)
        Tweak.__init__(self, title, "", **options)

        self.settings = Gio.Settings("org.gnome.desktop.peripherals.touchpad")
        self.key_name = "click-method"

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box.add_css_class("split-row")

        self.content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.content_box.add_css_class("content")

        label = Gtk.Label(halign=Gtk.Align.START, label=title)
        label.add_css_class("title")

        box.append(label)
        box.append(self.content_box)

        self.set_child(box)

        self.row_fingers = self._setup_row(
            key_name="fingers", title=_("Fingers"),
            subtitle=_(
                "Click the touchpad with two fingers for right-click and three fingers for middle-click."))

        self.row_area = self._setup_row(
            key_name="areas", title=_("Area"),
            subtitle=_(
                "Click the bottom right of the touchpad for right-click and the bottom middle for middle-click."))

        self.row_disabled= self._setup_row(
            key_name="none", title=_("Disabled"),
            subtitle=_(
                "Don’t use mouse click emulation."))

        self.row_area.set_group(self.row_fingers)
        self.row_disabled.set_group(self.row_fingers)

        self.settings.connect("changed", self._on_settings_changed)



    def _setup_row(self, key_name: str, title: str, subtitle: str) -> CheckPreferencesRow:
        row = CheckPreferencesRow(title, subtitle, key_name)
        row.btn.set_active(self.settings[self.key_name] == key_name)
        row.btn.connect("toggled", self._on_row_clicked, row)

        self.content_box.append(row)
        return row

    def _on_settings_changed(self, settings, key: str):
        keyvalue = settings[key]
        if keyvalue == "fingers":
            self.row_fingers.set_active(True)
        elif keyvalue == "areas":
            self.row_area.set_active(True)
        else:  # none
            self.row_disabled.set_active(True)

    def _on_row_clicked(self, _btn, action_row: CheckPreferencesRow):
        if self.settings[self.key_name] != action_row.keyvalue:
            self.settings[self.key_name] = action_row.keyvalue

TWEAK_GROUP = ListBoxTweakGroup("mouse", _("Mouse & Touchpad"),
  ListBoxTweakSubgroup(_("Mouse"), "mouse",
    GSettingsSwitchTweak(_("Middle Click Paste"),
                         "org.gnome.desktop.interface",
                         "gtk-enable-primary-paste"),
  ),
  ListBoxTweakSubgroup(_("Touchpad"), "touchpad",
    GSettingsSwitchTweak(_("Disable While Typing"),
                         "org.gnome.desktop.peripherals.touchpad",
                         "disable-while-typing",
                         schema_filename="org.gnome.desktop.peripherals.gschema.xml"),
    ClickMethod(),
  ),
)
