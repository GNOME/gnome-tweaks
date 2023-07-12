# Copyright (c) 2011 John Stowers
# SPDX-License-Identifier: GPL-3.0+
# License-Filename: LICENSES/GPL-3.0

import gtweak
from gtweak.widgets import ListBoxTweakGroup, GSettingsSwitchTweak, Title

TWEAK_GROUP = ListBoxTweakGroup("date-time", _("Date & Time"),
        Title(_("Clock"),""),
        GSettingsSwitchTweak(_("Show Weekday"),"org.gnome.desktop.interface", "clock-show-weekday"),
        GSettingsSwitchTweak(_("Show Date"),"org.gnome.desktop.interface", "clock-show-date"),
        GSettingsSwitchTweak(_("Show Seconds"), "org.gnome.desktop.interface", "clock-show-seconds"),
        Title(_("Calendar"),""),
        GSettingsSwitchTweak(_("Show Week Numbers"),"org.gnome.desktop.calendar", "show-weekdate"),
)
