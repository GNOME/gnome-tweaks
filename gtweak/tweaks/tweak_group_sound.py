# Copyright (c) 2017 Canonical
# SPDX-License-Identifier: GPL-3.0+
# License-Filename: LICENSES/GPL-3.0

import os
import configparser
from gtweak.utils import get_resource_dirs
from gtweak.widgets import ListBoxTweakGroup, GSettingsSwitchTweak, GSettingsComboTweak, Title

def get_theme_name(index_path):
    """Given an index file path, gets the relevant sound theme's name."""
    config = configparser.ConfigParser()
    config.read(index_path)
    return config["Sound Theme"]["Name"]

def get_sound_themes():
    """Gets the available sound themes as a (theme_directory_name, theme_display_name) tuple list."""
    themes = []
    for location in get_resource_dirs("sounds"):
        for item in os.listdir(location):
            candidate = os.path.join(location, item)
            index_file = os.path.join(candidate, "index.theme")
            if os.path.isdir(candidate) and os.path.exists(index_file):
                themes.append((os.path.basename(candidate), get_theme_name(index_file)))
    print(themes)
    return themes


TWEAK_GROUPS = [
    ListBoxTweakGroup(_("Sound"),
        GSettingsSwitchTweak(_("Over-Amplification"), "org.gnome.desktop.sound", "allow-volume-above-100-percent",
                        desc=_("Allows raising the volume above 100%. This can result in a loss of audio quality; it is better to increase application volume settings, if possible.")),
    Title(_("Event and input feedback sound settings"), _("Settings related to event and input feedback sounds.")),
    GSettingsSwitchTweak(_("Enable event sounds"), "org.gnome.desktop.sound", "event-sounds",
                        desc=_("This enables playback of sounds as a reaction to system events.")),
    GSettingsSwitchTweak(_("Enable input feedback sounds"), "org.gnome.desktop.sound", "input-feedback-sounds",
                        desc=_("This enables playback of sounds as a feedback to input events.")),
    GSettingsComboTweak(_("Sound theme"), "org.gnome.desktop.sound", "theme-name", get_sound_themes(),
                        desc=_("Specifies which sound theme to use for sound events."))
    )
]
