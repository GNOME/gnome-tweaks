from gi.repository import Gtk

from gtweak.tweakmodel import TweakGroup
from gtweak.widgets import GSettingsFontButtonTweak, build_horizontal_sizegroup

sg = build_horizontal_sizegroup()

TWEAK_GROUPS = (
        TweakGroup(
            "Fonts",
            GSettingsFontButtonTweak("org.gnome.desktop.interface", "font-name", size_group=sg),
            GSettingsFontButtonTweak("org.gnome.desktop.interface", "document-font-name", size_group=sg),
            GSettingsFontButtonTweak("org.gnome.desktop.interface", "monospace-font-name", size_group=sg)),
)
