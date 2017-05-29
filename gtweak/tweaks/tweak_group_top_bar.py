# This Python file uses the following encoding: utf-8
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
from gtweak.tweakmodel import TWEAK_GROUP_TOPBAR
from gtweak.widgets import ListBoxTweakGroup, GSettingsSwitchTweak, GSettingsCheckTweak, GetterSetterSwitchTweak, Title
from gtweak.utils import XSettingsOverrides

_shell = GnomeShellFactory().get_shell()
_shell_loaded = _shell is not None

class ApplicationMenuTweak(GetterSetterSwitchTweak):
    def __init__(self, **options):
        self._xsettings = XSettingsOverrides()
        GetterSetterSwitchTweak.__init__(self, _("Show Application Menu"), **options)

    def get_active(self):
        return self._xsettings.get_shell_shows_app_menu()

    def set_active(self, v):
        self._xsettings.set_shell_shows_app_menu(v)

TWEAK_GROUPS = [
    ListBoxTweakGroup(TWEAK_GROUP_TOPBAR,
        ApplicationMenuTweak(),
        Title(_("Clock"),""),
        GSettingsCheckTweak(_("Show date"),"org.gnome.desktop.interface", "clock-show-date", schema_filename="org.gnome.desktop.interface.gschema.xml"),
        GSettingsCheckTweak(_("Show seconds"), "org.gnome.desktop.interface", "clock-show-seconds", schema_filename="org.gnome.desktop.interface.gschema.xml"),
        Title(_("Calendar"),""),
        GSettingsCheckTweak(_("Show week numbers"),"org.gnome.desktop.calendar", "show-weekdate", schema_filename="org.gnome.desktop.calendar.gschema.xml"),
    )
]
