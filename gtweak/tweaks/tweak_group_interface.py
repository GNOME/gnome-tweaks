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

from gi.repository import Gtk
from gi.repository import GLib

import gtweak
from gtweak.utils import walk_directories, make_combo_list_with_default
from gtweak.tweakmodel import TWEAK_GROUP_APPEARANCE, TWEAK_GROUP_KEYBOARD
from gtweak.widgets import ListBoxTweakGroup, GSettingsSwitchTweak, GSettingsComboTweak, DarkThemeSwitcher, Title

class GtkThemeSwitcher(GSettingsComboTweak):
    def __init__(self, **options):
        GSettingsComboTweak.__init__(self,
			"GTK+",
            "org.gnome.desktop.interface",
            "gtk-theme",
            make_combo_list_with_default(self._get_valid_themes(), "Adwaita"),
            **options)

    def _get_valid_themes(self):
        """ Only shows themes that have variations for gtk+-3 and gtk+-2 """
        dirs = ( os.path.join(gtweak.DATA_DIR, "themes"),
                 os.path.join(GLib.get_user_data_dir(), "themes"),
                 os.path.join(os.path.expanduser("~"), ".themes"))
        valid = walk_directories(dirs, lambda d:
                    os.path.exists(os.path.join(d, "gtk-2.0")) and \
                        os.path.exists(os.path.join(d, "gtk-3.0")))
        return valid

class IconThemeSwitcher(GSettingsComboTweak):
    def __init__(self, **options):
        GSettingsComboTweak.__init__(self,
			"Icons",            
			"org.gnome.desktop.interface",
            "icon-theme",
            make_combo_list_with_default(self._get_valid_icon_themes(), "gnome"),
            **options)

    def _get_valid_icon_themes(self):
        dirs = ( os.path.join(gtweak.DATA_DIR, "icons"),
                 os.path.join(GLib.get_user_data_dir(), "icons"),
                 os.path.join(os.path.expanduser("~"), ".icons"))
        valid = walk_directories(dirs, lambda d:
                    os.path.isdir(d) and \
                        not os.path.exists(os.path.join(d, "cursors")))
        return valid

class CursorThemeSwitcher(GSettingsComboTweak):
    def __init__(self, **options):
        GSettingsComboTweak.__init__(self,
			"Cursor",
            "org.gnome.desktop.interface",
            "cursor-theme",
            make_combo_list_with_default(self._get_valid_cursor_themes(), "Adwaita"),
            **options)

    def _get_valid_cursor_themes(self):
        dirs = ( os.path.join(gtweak.DATA_DIR, "icons"),
                 os.path.join(GLib.get_user_data_dir(), "icons"),
                 os.path.join(os.path.expanduser("~"), ".icons"))
        valid = walk_directories(dirs, lambda d:
                    os.path.isdir(d) and \
                        os.path.exists(os.path.join(d, "cursors")))
        return valid

class KeyThemeSwitcher(GSettingsComboTweak):
    def __init__(self, **options):
        GSettingsComboTweak.__init__(self,
			"Key",
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

class WindowThemeSwitcher(GSettingsComboTweak):
    def __init__(self, **options):
        GSettingsComboTweak.__init__(self,
			"Window",
            "org.gnome.desktop.wm.preferences",
            "theme",
            make_combo_list_with_default(self._get_valid_themes(), "Adwaita"),
            **options)

    def _get_valid_themes(self):
        dirs = ( os.path.join(gtweak.DATA_DIR, "themes"),
                 os.path.join(GLib.get_user_data_dir(), "themes"))
        valid = walk_directories(dirs, lambda d:
                    os.path.exists(os.path.join(d, "metacity-1")))
        return valid



TWEAK_GROUPS = [
    ListBoxTweakGroup(TWEAK_GROUP_APPEARANCE,
        #GSettingsSwitchTweak("Buttons Icons","org.gnome.desktop.interface", "buttons-have-icons"),
        #GSettingsSwitchTweak("Menu Icons","org.gnome.desktop.interface", "menus-have-icons"),
        DarkThemeSwitcher(),
        Title("Theme", ""),
        WindowThemeSwitcher(),
        GtkThemeSwitcher(),
	IconThemeSwitcher(),
        CursorThemeSwitcher(),
    ),
    ListBoxTweakGroup(TWEAK_GROUP_KEYBOARD,
        KeyThemeSwitcher(),
    ),
]
