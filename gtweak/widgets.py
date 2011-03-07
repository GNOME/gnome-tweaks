from gi.repository import Gtk, Gio

from gtweak.tweakmodel import Tweak
from gtweak.gsettings import GSettingsSetting

def build_label_beside_widget(txt, widget, hbox=None):
    if not hbox:
        hbox = Gtk.HBox()
    lbl = Gtk.Label(txt)
    lbl.props.xalign = 0.0
    hbox.pack_start(lbl, True, False, 0)
    hbox.pack_start(widget, False, False, 0)
    return hbox

def build_combo_box_text(selected, *values):
    store = Gtk.ListStore(str, str)

    selected_iter = None
    for (val, name) in values:
        _iter = store.append( (val, name) )
        if val == selected:
            selected_iter = _iter

    combo = Gtk.ComboBox(model=store)
    renderer = Gtk.CellRendererText()
    combo.pack_start(renderer, True)
    combo.add_attribute(renderer, 'text', 1)
    if selected_iter:
        combo.set_active_iter(selected_iter)

    return combo

class GSettingsSwitch(Gtk.HBox):
    def __init__(self, settings, key):
        Gtk.HBox.__init__(self)
        self._settings = settings

        self._sw = Gtk.Switch()
        self._settings.bind(key, self._sw, "active", Gio.SettingsBindFlags.DEFAULT)

        build_label_beside_widget(self._settings.schema_get_summary(key), self._sw, self)
        self.show_all()

class GSettingsSwitchTweak(Tweak):
    def __init__(self, schema_name, key_name):
        settings = GSettingsSetting(schema_name)
        Tweak.__init__(self, settings.schema_get_summary(key_name), settings.schema_get_description(key_name))
        self.widget = GSettingsSwitch(settings, key_name)


