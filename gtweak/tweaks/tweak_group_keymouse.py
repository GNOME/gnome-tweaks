# This file is part of gnome-tweak-tool.
#
# Copyright (c) 2011 John Stowers
#
# gnome-tweak-tool is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# gnome-tweak-tool is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with gnome-tweak-tool.  If not, see <http://www.gnu.org/licenses/>.

import os.path

from gi.repository import GLib, Gtk, Gdk

import gtweak
from gtweak.widgets import ListBoxTweakGroup, GSettingsSwitchTweak, GSettingsSwitchTweakValue, _GSettingsTweak, Title, GSettingsComboEnumTweak, build_label_beside_widget, Tweak

from gtweak.tweaks.tweak_group_xkb import TypingTweakGroup

class KeyThemeSwitcher(GSettingsSwitchTweakValue):
    def __init__(self, **options):
        GSettingsSwitchTweakValue.__init__(self,
                                           _("Emacs Input"),
                                           "org.gnome.desktop.interface",
                                           "gtk-key-theme",
                                           **options)

    def get_active(self):
        return "Emacs" in self.settings.get_string(self.key_name)

    def set_active(self, v):
        if v:
            self.settings.set_string(self.key_name, "Emacs")
        else:
            self.settings.set_string(self.key_name, "Default")

class OverviewShortcutTweak(Gtk.Box, _GSettingsTweak):

    def __init__(self, **options):
        name = _("Overview Shortcut")
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        _GSettingsTweak.__init__(self, name, "org.gnome.mutter", "overlay-key", **options)

        box_btn = Gtk.ButtonBox()
        box_btn.set_layout(Gtk.ButtonBoxStyle.EXPAND)

        btn1 = Gtk.RadioButton.new_with_label_from_widget(None, _("Left Super"))
        btn1.set_property("draw-indicator", False)

        btn2 = Gtk.RadioButton.new_from_widget(btn1)
        btn2.set_label(_("Right Super"))
        btn2.set_property("draw-indicator", False)

        if (self.settings.get_string(self.key_name) == "Super_R"):
            btn2.set_active(True)
        btn1.connect("toggled", self.on_button_toggled, "Super_L")
        btn2.connect("toggled", self.on_button_toggled, "Super_R")

        box_btn.pack_start(btn1, True, True, 0)
        box_btn.pack_start(btn2, True, True, 0)
        build_label_beside_widget(name, box_btn, hbox=self)

    def on_button_toggled(self, button, key):
        self.settings[self.key_name] = key


class AdditionalLayoutButton(Gtk.Box, Tweak):

    def __init__(self):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL, spacing=18,
                               valign=Gtk.Align.CENTER)
        Tweak.__init__(self, 'extensions', '')

        btn = Gtk.Button(label=_("Additional Layout Options"),halign=Gtk.Align.END)
        btn.connect("clicked", self._on_browse_clicked)
        self.add(btn)

        self.show_all()

    def _on_browse_clicked(self, btn):
        dialog = Gtk.Window()
        dialog.set_title(_("Additional Layout Options"))
        dialog.set_type_hint(Gdk.WindowTypeHint.DIALOG)
        dialog.set_transient_for(self.main_window)
        dialog.set_modal(True)

        dialog.set_size_request(500,500)
        geometry = Gdk.Geometry()
        geometry.max_height = 500
        dialog.set_geometry_hints(None, geometry, Gdk.WindowHints.MAX_SIZE)

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_border_width(10)
        box = TypingTweakGroup()
        scrolled_window.add_with_viewport(box)

        dialog.add(scrolled_window)
        dialog.show_all()


TWEAK_GROUPS = [
    ListBoxTweakGroup(_("Keyboard & Mouse"),
        Title(_("Keyboard"), ""),
        GSettingsSwitchTweak(_("Show Extended Input Sources"),
                              "org.gnome.desktop.input-sources",
                              "show-all-sources",
                              desc=_("Increases the choice of input sources in the Settings application."),
                              logout_required=True,),
        KeyThemeSwitcher(),
        OverviewShortcutTweak(),
        AdditionalLayoutButton(),
        Title(_("Mouse"), ""),
        GSettingsComboEnumTweak(_("Acceleration Profile"),
                                "org.gnome.desktop.peripherals.mouse",
                                "accel-profile",
                                schema_filename="org.gnome.desktop.peripherals.gschema.xml"),
        GSettingsSwitchTweak(_("Pointer Location"),
                             "org.gnome.settings-daemon.peripherals.mouse", 
                             "locate-pointer", 
                              schema_filename="org.gnome.settings-daemon.peripherals.gschema.xml",
                              desc=_("Press the Ctrl key to highlight the pointer.")),
        GSettingsSwitchTweak(_("Middle Click Paste"),
                             "org.gnome.desktop.interface",
                             "gtk-enable-primary-paste"),

        Title(_("Touchpad"), ""),
        GSettingsComboEnumTweak(_("Click Method"),
                                "org.gnome.desktop.peripherals.touchpad",
                                "click-method",
                                schema_filename="org.gnome.desktop.peripherals.gschema.xml"),
        GSettingsSwitchTweak(_("Disable While Typing"),
                             "org.gnome.desktop.peripherals.touchpad",
                             "disable-while-typing",
                             schema_filename="org.gnome.desktop.peripherals.gschema.xml"),
        ),
]
