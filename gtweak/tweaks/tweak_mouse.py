from gtweak.tweakmodel import TWEAK_GROUP_MOUSE
from gtweak.widgets import GSettingsSwitchTweak

TWEAKS = (
    GSettingsSwitchTweak("Show location of pointer",
                         "org.gnome.settings-daemon.peripherals.mouse",
                         "locate-pointer",
                         schema_filename="org.gnome.settings-daemon.peripherals.gschema.xml",
                         group_name=TWEAK_GROUP_MOUSE),
)
