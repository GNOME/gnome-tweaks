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

import gtweak
from gtweak.utils import walk_directories, make_combo_list_with_default
from gtweak.tweakmodel import TweakGroup
from gtweak.widgets import GConfComboTweak, build_horizontal_sizegroup
from gtweak.gconf import GConfSetting

class ActionClickTitlebarTweak(GConfComboTweak):
    def __init__(self, key_name, **options):

        #from the metacity schema
        schema_options = ('toggle_shade', 'toggle_maximize', 'toggle_maximize_horizontally',
                          'toggle_maximize_vertically', 'minimize', 'shade', 'menu', 'lower', 'none')

        GConfComboTweak.__init__(self,
            key_name,
            str,
            [(o, o.replace("_"," ").title()) for o in schema_options],
            **options)

class FocusModeTweak(GConfComboTweak):
    def __init__(self, **options):
        GConfComboTweak.__init__(self,
            "/apps/metacity/general/focus_mode",
            str,
            [(o, o.title()) for o in ("click","sloppy","mouse")],
            **options)

class WindowThemeSwitcher(GConfComboTweak):
    def __init__(self, **options):
        GConfComboTweak.__init__(self,
            "/desktop/gnome/shell/windows/theme",
            str,
            make_combo_list_with_default(self._get_valid_themes(), "Adwaita"),
            **options)

        #also need to change the fallback (metacity) window theme
        self.gconf_metacity = GConfSetting("/apps/metacity/general/theme", str)

    def _get_valid_themes(self):
        dirs = ( os.path.join(gtweak.DATA_DIR, "themes"),
                 os.path.join(os.path.expanduser("~"), ".themes"))
        valid = walk_directories(dirs, lambda d:
                    os.path.exists(os.path.join(d, "metacity-1")))
        return valid

    def _on_combo_changed(self, combo):
        #its probbably not too nice to dupe this function here, but i'm lazy
        #and the real cause is the hidious gconf/shell/metacity override business
        _iter = combo.get_active_iter()
        if _iter:
            value = combo.get_model().get_value(_iter, 0)
            self.gconf.set_value(value)
            self.gconf_metacity.set_value(value)

sg = build_horizontal_sizegroup()

TWEAK_GROUPS = (
        TweakGroup(
            "Windows",
            WindowThemeSwitcher(size_group=sg),
            ActionClickTitlebarTweak("/apps/metacity/general/action_double_click_titlebar", size_group=sg),
            ActionClickTitlebarTweak("/apps/metacity/general/action_middle_click_titlebar", size_group=sg),
            ActionClickTitlebarTweak("/apps/metacity/general/action_right_click_titlebar", size_group=sg),
            FocusModeTweak(size_group=sg)),
)
