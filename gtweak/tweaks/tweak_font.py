from gi.repository import Gtk

from gtweak.tweakmodel import TweakGroup
from gtweak.widgets import GSettingsFontButtonTweak

TWEAK_GROUPS = (
        TweakGroup(
            "Fonts",
            GSettingsFontButtonTweak("org.gnome.desktop.interface", "font-name"),
            GSettingsFontButtonTweak("org.gnome.desktop.interface", "document-font-name"),
            GSettingsFontButtonTweak("org.gnome.desktop.interface", "monospace-font-name")),
)
