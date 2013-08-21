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

from gi.repository import GLib, Gtk

import gtweak
from gtweak.tweakmodel import Tweak
from gtweak.utils import XSettingsOverrides, walk_directories, make_combo_list_with_default
from gtweak.widgets import ListBoxTweakGroup, GSettingsComboTweak, GSettingsSwitchTweak, Title, build_label_beside_widget

class PrimaryPasteTweak(Gtk.Box, Tweak):
    def __init__(self, **options):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.HORIZONTAL)

        name = _("Middle-click Paste")
        description = ""
        Tweak.__init__(self, name, description, **options)

        self._xsettings = XSettingsOverrides()

        sw = Gtk.Switch()
        sw.set_active(self._xsettings.get_enable_primary_paste())
        sw.connect("notify::active", self._on_toggled)

        build_label_beside_widget(
                name,
                sw,
                hbox=self)


    def _on_toggled(self, sw, pspec):
        self._xsettings.set_enable_primary_paste(sw.get_active())

class KeyThemeSwitcher(GSettingsComboTweak):
    def __init__(self, **options):
        GSettingsComboTweak.__init__(self,
			_("Key theme"),
            "org.gnome.desktop.interface",
            "gtk-key-theme",
            make_combo_list_with_default(
                self._get_valid_key_themes(),
                "Default",
                default_text=_("<i>Default</i>")),
            **options)

    def _get_valid_key_themes(self):
        dirs = ( os.path.join(gtweak.DATA_DIR, "themes"),
                 os.path.join(GLib.get_user_data_dir(), "themes"),
                 os.path.join(os.path.expanduser("~"), ".themes"))
        valid = walk_directories(dirs, lambda d:
                    os.path.isfile(os.path.join(d, "gtk-3.0", "gtk-keys.css")) and \
                    os.path.isfile(os.path.join(d, "gtk-2.0-key", "gtkrc")))
        return valid

TWEAK_GROUPS = [
    ListBoxTweakGroup(_("Keyboard and Mouse"),
        KeyThemeSwitcher(),
        Title(_("Mouse"), ""),
        GSettingsSwitchTweak(_("Show location of pointer"),
                             "org.gnome.settings-daemon.peripherals.mouse", 
                             "locate-pointer", 
                              schema_filename="org.gnome.settings-daemon.peripherals.gschema.xml"),
        PrimaryPasteTweak(),
        ),
]
