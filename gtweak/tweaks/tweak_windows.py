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

from gtweak.tweakmodel import TweakGroup
from gtweak.widgets import GConfComboTweak, build_horizontal_sizegroup

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

sg = build_horizontal_sizegroup()

TWEAK_GROUPS = (
        TweakGroup(
            "Windows",
            ActionClickTitlebarTweak("/apps/metacity/general/action_double_click_titlebar", size_group=sg),
            ActionClickTitlebarTweak("/apps/metacity/general/action_middle_click_titlebar", size_group=sg),
            ActionClickTitlebarTweak("/apps/metacity/general/action_right_click_titlebar", size_group=sg)),
)
