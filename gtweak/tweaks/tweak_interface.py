from gi.repository import Gtk

from gtweak.tweakmodel import TweakGroup
from gtweak.widgets import GSettingsSwitchTweak

TWEAK_GROUPS = (
        TweakGroup(
            "Interface",
            GSettingsSwitchTweak("org.gnome.desktop.interface", "menus-have-icons"),
            GSettingsSwitchTweak("org.gnome.desktop.interface", "buttons-have-icons")),
)
