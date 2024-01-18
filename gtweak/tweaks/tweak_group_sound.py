# Copyright (c) 2011 John Stowers
# SPDX-License-Identifier: GPL-3.0+
# License-Filename: LICENSES/GPL-3.0

import os
import os.path
import configparser


from gtweak.utils import get_resource_dirs
from gtweak.widgets import TweakPreferencesPage, GSettingsTweakComboRow


def get_theme_name(index_path):
    """Given an index file path, gets the relevant sound theme's name."""
    config = configparser.ConfigParser()
    config.read(index_path)
    return config["Sound Theme"]["Name"]


def get_sound_themes():
    """Gets the available sound themes as a (theme_directory_name, theme_display_name) tuple list."""
    themes = []
    seen = set()
    for location in get_resource_dirs("sounds"):
        for item in os.listdir(location):
            candidate = os.path.join(location, item)
            index_file = os.path.join(candidate, "index.theme")
            if os.path.isdir(candidate) and os.path.exists(index_file):
                theme_info = (os.path.basename(candidate), get_theme_name(index_file))
                if theme_info[1] not in seen:
                    themes.append(theme_info)
                    seen.add(theme_info[1])
    return themes

sound_themes = get_sound_themes()

show_sound_tweaks = len(sound_themes) > 0

TWEAK_GROUP = TweakPreferencesPage(
    "sound",
    _("Sound"),
    GSettingsTweakComboRow(
        _("System Sound Theme"),
        "org.gnome.desktop.sound",
        "theme-name",
        sound_themes,
        desc=_("Specifies which sound theme to use for sound events."),
    ),
)





