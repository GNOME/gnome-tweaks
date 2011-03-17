from gi.repository import Gtk

from gtweak.tweakmodel import Tweak, TweakGroup
from gtweak.gconf import GConfSetting
from gtweak.widgets import GSettingsRangeTweak, GSettingsFontButtonTweak, build_horizontal_sizegroup, build_label_beside_widget

class MetacityTitleFont(Tweak):
    def __init__(self, **options):
        self._gconf = GConfSetting("/apps/metacity/general/titlebar_font", str)
        Tweak.__init__(self, self._gconf.schema_get_summary(), self._gconf.schema_get_description(), **options)

        w = Gtk.FontButton()
        w.props.font_name = self._gconf.get_value()
        w.connect("notify::font-name", self._on_fontbutton_changed)
        self.widget = build_label_beside_widget(self._gconf.schema_get_summary(), w)
        self.widget_for_size_group = w

    def _on_fontbutton_changed(self, btn, param):
        self._gconf.set_value(btn.props.font_name)

sg = build_horizontal_sizegroup()

TWEAK_GROUPS = (
        TweakGroup(
            "Fonts",
            GSettingsRangeTweak("org.gnome.desktop.interface", "text-scaling-factor", adjustment_step=0.1, size_group=sg),
            GSettingsFontButtonTweak("org.gnome.desktop.interface", "font-name", size_group=sg),
            GSettingsFontButtonTweak("org.gnome.desktop.interface", "document-font-name", size_group=sg),
            GSettingsFontButtonTweak("org.gnome.desktop.interface", "monospace-font-name", size_group=sg),
            MetacityTitleFont(size_group=sg)),
)
