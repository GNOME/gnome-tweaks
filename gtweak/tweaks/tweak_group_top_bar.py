# Copyright (c) 2011 John Stowers
# SPDX-License-Identifier: GPL-3.0+
# License-Filename: LICENSES/GPL-3.0

import gtweak
from gtweak.gshellwrapper import GnomeShellFactory
from gtweak.widgets import ListBoxTweakGroup, GSettingsSwitchTweak, Title

_shell = GnomeShellFactory().get_shell()
_shell_loaded = _shell is not None


TWEAK_GROUPS = [
    ListBoxTweakGroup(_("Top Bar"),
        GSettingsSwitchTweak(_("Activities Overview Hot Corner"),"org.gnome.desktop.interface", "enable-hot-corners", loaded=_shell_loaded),
        GSettingsSwitchTweak(_("Battery Percentage"),"org.gnome.desktop.interface", "show-battery-percentage", loaded=_shell_loaded),
        Title(_("Clock"),"", loaded=_shell_loaded),
        GSettingsSwitchTweak(_("Weekday"),"org.gnome.desktop.interface", "clock-show-weekday", loaded=_shell_loaded),
        GSettingsSwitchTweak(_("Date"),"org.gnome.desktop.interface", "clock-show-date", loaded=_shell_loaded),
        GSettingsSwitchTweak(_("Seconds"), "org.gnome.desktop.interface", "clock-show-seconds", loaded=_shell_loaded),
        Title(_("Calendar"),"", loaded=_shell_loaded),
        GSettingsSwitchTweak(_("Week Numbers"),"org.gnome.desktop.calendar", "show-weekdate", loaded=_shell_loaded),
    )
]
