import os.path

from gi.repository import Gtk

import gtweak
from gtweak.tweakmodel import TweakGroup
from gtweak.widgets import GSettingsSwitchTweak, GSettingsComboTweak

class ThemeSwitcher(GSettingsComboTweak):
    """ Only shows themes that have variations for gtk+-3 and gtk+-2 """
    def __init__(self, **options):
        valid_themes = []
        themedir = os.path.join(gtweak.DATA_DIR, "themes")
        for t in os.listdir(themedir):
            if os.path.exists(os.path.join(themedir, t, "gtk-2.0")) and \
               os.path.exists(os.path.join(themedir, t, "gtk-3.0")):
                valid_themes.append(t)

        GSettingsComboTweak.__init__(self,
            "org.gnome.desktop.interface",
            "gtk-theme",
            [(t, t) for t in valid_themes],
            **options)

TWEAK_GROUPS = (
        TweakGroup(
            "Interface",
            GSettingsSwitchTweak("org.gnome.desktop.interface", "menus-have-icons"),
            GSettingsSwitchTweak("org.gnome.desktop.interface", "buttons-have-icons"),
            ThemeSwitcher()),
)
