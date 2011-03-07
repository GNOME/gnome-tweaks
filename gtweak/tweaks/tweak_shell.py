from gi.repository import Gtk

from gtweak.gconf import GConfSetting
from gtweak.tweakmodel import Tweak, TweakGroup
from gtweak.widgets import build_label_beside_widget, build_combo_box_text

class ShowWindowButtons(Tweak):
    def __init__(self):
        Tweak.__init__(self, "Window buttons", "Should the maximize and minimize buttons be shown")

        self._gconf = GConfSetting("/desktop/gnome/shell/windows/button_layout", str)

        combo = build_combo_box_text(
            self._gconf.get_value(),
            (':close', 'Close Only'),
            (':minimize,close', 'Minimize and Close'),
            (':maximize,close', 'Maximize and Close'),
            (':minimize,maximize,close', 'All'))
        combo.connect('changed', self._on_combo_changed)
        self.widget = build_label_beside_widget(self.name, combo)

    def _on_combo_changed(self, combo):
        _iter = combo.get_active_iter()
        if _iter:
            value = combo.get_model().get_value(_iter, 0)
            print "selected", value
            self._gconf.set_value(value)

TWEAK_GROUPS = (
        TweakGroup(
            "GNOME Shell",
            ShowWindowButtons()),
)
