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

from gi.repository import GLib

import gtweak
from gtweak.widgets import ListBoxTweakGroup, GSettingsComboTweak, GSettingsSwitchTweak, GSettingsSwitchTweakValue, GetterSetterSwitchTweak, Title, GSettingsComboEnumTweak

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

TWEAK_GROUPS = [
    ListBoxTweakGroup(_("Keyboard & Mouse"),
        GSettingsSwitchTweak(_("Show Extended Input Sources"),
                              "org.gnome.desktop.input-sources",
                              "show-all-sources",
                              desc=_("Increases the choice of input sources in the Settings application."),
                              logout_required=True,),
        KeyThemeSwitcher(),
        GSettingsComboTweak(_("Switch between overview and desktop"),
                              "org.gnome.mutter",
                              "overlay-key",
                              [("Super_L", _("Left super")), ("Super_R", _("Right super"))]),
              
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
        ),
]
