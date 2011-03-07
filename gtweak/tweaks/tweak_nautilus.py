from gi.repository import Gtk

from gtweak.gsettings import GSettingsSetting
from gtweak.tweakmodel import Tweak, TweakGroup
from gtweak.widgets import GSettingsSwitch

class GSettingsSwitchTweak(Tweak):
    def __init__(self, schema_name, key_name):
        settings = GSettingsSetting(schema_name)
        Tweak.__init__(self, settings.schema_get_summary(key_name), settings.schema_get_description(key_name))
        self.widget = GSettingsSwitch(settings, key_name)

TWEAK_GROUPS = (
        TweakGroup(
            "Nautilus",
            GSettingsSwitchTweak("org.gnome.desktop.background", "show-desktop-icons"),
            GSettingsSwitchTweak("org.gnome.desktop.background", "draw-background")),
)
