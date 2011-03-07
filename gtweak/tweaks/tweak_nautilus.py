from gi.repository import Gtk

from gtweak.tweakmodel import TweakGroup
from gtweak.widgets import GSettingsSwitchTweak

TWEAK_GROUPS = (
        TweakGroup(
            "Nautilus",
            GSettingsSwitchTweak("org.gnome.desktop.background", "show-desktop-icons"),
            GSettingsSwitchTweak("org.gnome.desktop.background", "draw-background")),
)
