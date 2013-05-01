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
from gtweak.utils import walk_directories, make_combo_list_with_default
from gtweak.tweakmodel import TWEAK_GROUP_WINDOWS, TWEAK_GROUP_THEME
from gtweak.widgets import GSettingsComboTweak, GSettingsComboEnumTweak, GSettingsSwitchTweak

class WindowThemeSwitcher(GSettingsComboTweak):
    def __init__(self, **options):
        GSettingsComboTweak.__init__(self,
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

TWEAKS = (
    WindowThemeSwitcher(group_name=TWEAK_GROUP_THEME),
    GSettingsComboEnumTweak("org.gnome.desktop.wm.preferences", "action-double-click-titlebar", group_name=TWEAK_GROUP_WINDOWS),
    GSettingsComboEnumTweak("org.gnome.desktop.wm.preferences", "action-middle-click-titlebar", group_name=TWEAK_GROUP_WINDOWS),
    GSettingsComboEnumTweak("org.gnome.desktop.wm.preferences", "action-right-click-titlebar", group_name=TWEAK_GROUP_WINDOWS),
    GSettingsComboEnumTweak("org.gnome.desktop.wm.preferences", "focus-mode", group_name=TWEAK_GROUP_WINDOWS),
    GSettingsComboTweak("org.gnome.desktop.wm.preferences",
                        "mouse-button-modifier",
                        [("disabled", _("Disabled")), ("<Alt>", "Alt"), ("<Super>", "Super")],
                        group_name=TWEAK_GROUP_WINDOWS),
    GSettingsSwitchTweak("org.gnome.desktop.wm.preferences", "resize-with-right-button", group_name=TWEAK_GROUP_WINDOWS),
    GSettingsSwitchTweak("org.gnome.desktop.wm.preferences", "raise-on-click", group_name=TWEAK_GROUP_WINDOWS),
)
