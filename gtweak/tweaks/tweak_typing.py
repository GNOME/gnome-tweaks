from gtweak.tweakmodel import TWEAK_GROUP_TYPING
from gtweak.widgets import GSettingsComboEnumTweak

TWEAKS = (
    GSettingsComboEnumTweak("org.gnome.settings-daemon.peripherals.keyboard",
                            "input-sources-switcher",
                            schema_filename="org.gnome.settings-daemon.peripherals.gschema.xml",
                            group_name=TWEAK_GROUP_TYPING),
)
