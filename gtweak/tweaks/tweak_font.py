from gi.repository import Gtk

from gtweak.tweakmodel import TweakGroup
from gtweak.widgets import GSettingsRangeTweak, GSettingsFontButtonTweak, build_horizontal_sizegroup

sg = build_horizontal_sizegroup()

TWEAK_GROUPS = (
        TweakGroup(
            "Fonts",
#            GSettingsRangeTweak("org.gnome.desktop.interface", "text-scaling-factor", adjustment_step=0.1, size_group=sg),
            GSettingsFontButtonTweak("org.gnome.desktop.interface", "font-name", size_group=sg),
            GSettingsFontButtonTweak("org.gnome.desktop.interface", "document-font-name", size_group=sg),
            GSettingsFontButtonTweak("org.gnome.desktop.interface", "monospace-font-name", size_group=sg)),
)
