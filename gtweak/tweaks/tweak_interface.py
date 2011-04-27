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

import gtweak
from gtweak.utils import walk_directories
from gtweak.tweakmodel import TweakGroup
from gtweak.widgets import GSettingsSwitchTweak, GSettingsComboTweak, build_horizontal_sizegroup

class GtkThemeSwitcher(GSettingsComboTweak):
    def __init__(self, **options):
        GSettingsComboTweak.__init__(self,
            "org.gnome.desktop.interface",
            "gtk-theme",
            [(t, t) for t in self._get_valid_themes()],
            **options)

    def _get_valid_themes(self):
        """ Only shows themes that have variations for gtk+-3 and gtk+-2 """
        dirs = ( os.path.join(gtweak.DATA_DIR, "themes"),
                 os.path.join(os.path.expanduser("~"), ".themes"))
        valid = walk_directories(dirs, lambda d:
                    os.path.exists(os.path.join(d, "gtk-2.0")) and \
                        os.path.exists(os.path.join(d, "gtk-3.0")))
        return valid

class IconThemeSwitcher(GSettingsComboTweak):
    def __init__(self, **options):
        GSettingsComboTweak.__init__(self,
            "org.gnome.desktop.interface",
            "icon-theme",
            [(t, t) for t in self._get_valid_icon_themes()],
            **options)

    def _get_valid_icon_themes(self):
        dirs = ( os.path.join(gtweak.DATA_DIR, "icons"),
                 os.path.join(os.path.expanduser("~"), ".icons"))
        valid = walk_directories(dirs, lambda d:
                    os.path.isdir(d) and \
                        not os.path.exists(os.path.join(d, "cursors")))
        return valid

class CursorThemeSwitcher(GSettingsComboTweak):
    def __init__(self, **options):
        GSettingsComboTweak.__init__(self,
            "org.gnome.desktop.interface",
            "cursor-theme",
            [(t, t) for t in self._get_valid_cursor_themes()],
            **options)

    def _get_valid_cursor_themes(self):
        dirs = ( os.path.join(gtweak.DATA_DIR, "icons"),
                 os.path.join(os.path.expanduser("~"), ".icons"))
        valid = walk_directories(dirs, lambda d:
                    os.path.isdir(d) and \
                        os.path.exists(os.path.join(d, "cursors")))
        return valid

sg = build_horizontal_sizegroup()

TWEAK_GROUPS = (
        TweakGroup(
            "Interface",
            GSettingsSwitchTweak("org.gnome.desktop.interface", "menus-have-icons"),
            GSettingsSwitchTweak("org.gnome.desktop.interface", "buttons-have-icons"),
            GtkThemeSwitcher(size_group=sg),
            IconThemeSwitcher(size_group=sg),
            CursorThemeSwitcher(size_group=sg)),
)
