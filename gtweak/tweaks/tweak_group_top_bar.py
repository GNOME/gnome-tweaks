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
from gtweak.widgets import ListBoxTweakGroup, GSettingsSwitchTweak, GetterSetterSwitchTweak, Title, _GSettingsTweak
from gtweak.utils import XSettingsOverrides

_shell = GnomeShellFactory().get_shell()
_shell_loaded = _shell is not None

class ApplicationMenuTweak(GetterSetterSwitchTweak):
    def __init__(self, **options):
        self._xsettings = XSettingsOverrides()
        name = _("Application Menu")
        GetterSetterSwitchTweak.__init__(self, name, **options)

        _GSettingsTweak.__init__(self,
                                 name,
                                 "org.gnome.desktop.wm.preferences",
                                 "button-layout",
                                 loaded=_shell_loaded,
                                 **options)

    def get_active(self):
        return self._xsettings.get_shell_shows_app_menu()

    def set_active(self, v):
        self._xsettings.set_shell_shows_app_menu(v)

        if v:
            self.notify_logout()
            return
        val = self.settings.get_string(self.key_name)
        if "appmenu" in val:
            self.notify_logout()
            return
        else:
            (left, colon, right) = val.partition(":")

            if "close" in right:
                rsplit = right.split(",")
                rsplit = [x for x in rsplit if x in ["minimize", "maximize", "close"]]
                rsplit.append("appmenu")
                rsplit.sort(key=lambda x: ["appmenu", "minimize", "maximize", "close"].index(x))
                self.settings.set_string(self.key_name, left + colon + ",".join(rsplit))

            else:
                rsplit = left.split(",")
                rsplit = [x for x in rsplit if x in ["minimize", "maximize", "close"]]
                rsplit.append("appmenu")
                rsplit.sort(key=lambda x: ["close", "minimize", "maximize", "appmenu"].index(x))
                self.settings.set_string(self.key_name, ",".join(rsplit) + colon + right)
        self.notify_logout()


TWEAK_GROUPS = [
    ListBoxTweakGroup(_("Top Bar"),
        ApplicationMenuTweak(),
        GSettingsSwitchTweak(_("Battery Percentage"),"org.gnome.desktop.interface", "show-battery-percentage", loaded=_shell_loaded),
        Title(_("Clock"),"", loaded=_shell_loaded),
        GSettingsSwitchTweak(_("Date"),"org.gnome.desktop.interface", "clock-show-date", loaded=_shell_loaded),
        GSettingsSwitchTweak(_("Seconds"), "org.gnome.desktop.interface", "clock-show-seconds", loaded=_shell_loaded),
        Title(_("Calendar"),"", loaded=_shell_loaded),
        GSettingsSwitchTweak(_("Week Numbers"),"org.gnome.desktop.calendar", "show-weekdate", loaded=_shell_loaded),
    )
]
