import os.path

from gi.repository import Gtk

import gtweak
from gtweak.tweakmodel import Tweak, TweakGroup
from gtweak.widgets import GSettingsSwitchTweak, build_label_beside_widget, build_combo_box_text
from gtweak.gsettings import GSettingsSetting



class ThemeSwitcher(Tweak):
    """ Only shows themes that have variations for gtk+-3 and gtk+-2 """
    def __init__(self, **options):
        self.key_name = "gtk-theme"
        self.settings = GSettingsSetting("org.gnome.desktop.interface")
        Tweak.__init__(self,
            self.settings.schema_get_summary(self.key_name),
            self.settings.schema_get_description(self.key_name),
            **options)
        
        valid_themes = []
        themedir = os.path.join(gtweak.DATA_DIR, "themes")
        for t in os.listdir(themedir):
            if os.path.exists(os.path.join(themedir, t, "gtk-2.0")) and \
               os.path.exists(os.path.join(themedir, t, "gtk-3.0")):
                valid_themes.append(t)
        
        combo = build_combo_box_text(
                    self.settings.get_value(self.key_name),
                    *[(t, t) for t in valid_themes])
        combo.connect('changed', self._on_combo_changed)
        self.widget = build_label_beside_widget(self.name, combo)

    def _on_combo_changed(self, combo):
        _iter = combo.get_active_iter()
        if _iter:
            value = combo.get_model().get_value(_iter, 0)
            self.settings.set_value(self.key_name, value)

TWEAK_GROUPS = (
        TweakGroup(
            "Interface",
            GSettingsSwitchTweak("org.gnome.desktop.interface", "menus-have-icons"),
            GSettingsSwitchTweak("org.gnome.desktop.interface", "buttons-have-icons"),
            ThemeSwitcher()),
)
