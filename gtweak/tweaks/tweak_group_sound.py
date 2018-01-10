# Copyright (c) 2017 Canonical
# SPDX-License-Identifier: GPL-3.0+
# License-Filename: LICENSES/GPL-3.0

from gi.repository import Gio, GLib, Gtk

import gtweak
from gtweak.tweakmodel import Tweak
from gtweak.widgets import ListBoxTweakGroup, GSettingsSwitchTweak

TWEAK_GROUPS = [
    ListBoxTweakGroup(_("Sound"),
        GSettingsSwitchTweak(_("Over-Amplification"), "org.gnome.desktop.sound", "allow-volume-above-100-percent",
                        desc=_("Allows raising the volume above 100%. This can result in a loss of audio quality; it is better to increase application volume settings, if possible.")),
    )
]
