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

import gtweak
from gtweak.gshellwrapper import GnomeShellFactory
from gtweak.tweakmodel import TWEAK_GROUP_WINDOWS
from gtweak.widgets import ListBoxTweakGroup, GSettingsComboEnumTweak, GSettingsComboTweak, Title

_shell = GnomeShellFactory().get_shell()
_shell_loaded = _shell is not None

class ShowWindowButtons(GSettingsComboTweak):
    def __init__(self, **options):
        GSettingsComboTweak.__init__(self,
			"Title Bar Buttons",
            "org.gnome.desktop.wm.preferences",
            "button-layout",
            ((':close', _("Close Only")),
            (':minimize,close', _("Minimize and Close")),
            (':maximize,close', _("Maximize and Close")),
            (':minimize,maximize,close', _("All"))),
            loaded=_shell_loaded,
            **options)

TWEAK_GROUPS = [ 
    ListBoxTweakGroup(TWEAK_GROUP_WINDOWS,
        GSettingsComboEnumTweak("Focus Mode", "org.gnome.desktop.wm.preferences", "focus-mode"),
        Title("Titlebar Actions", "", uid="title-titlebar-actions"),
        GSettingsComboEnumTweak("Double-click","org.gnome.desktop.wm.preferences", "action-double-click-titlebar"),
        GSettingsComboEnumTweak("Middle-click","org.gnome.desktop.wm.preferences", "action-middle-click-titlebar"),
        GSettingsComboEnumTweak("Secondary-click","org.gnome.desktop.wm.preferences", "action-right-click-titlebar"),
        ShowWindowButtons(group_name=TWEAK_GROUP_WINDOWS),
    )
]

