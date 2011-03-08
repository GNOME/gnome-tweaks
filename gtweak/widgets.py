from gi.repository import Gtk, Gio

from gtweak.tweakmodel import Tweak
from gtweak.gsettings import GSettingsSetting

def build_label_beside_widget(txt, widget, hbox=None):
    if not hbox:
        hbox = Gtk.HBox()
    lbl = Gtk.Label(txt)
    lbl.props.xalign = 0.0
    hbox.pack_start(lbl, True, True, 0)
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

def build_horizontal_sizegroup():
    sg = Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL)
    sg.props.ignore_hidden = True
    return sg

class _GSettingsTweak(Tweak):
    def __init__(self, schema_name, key_name, **options):
        self.settings = GSettingsSetting(schema_name)
        Tweak.__init__(self,
            self.settings.schema_get_summary(key_name),
            self.settings.schema_get_description(key_name),
            **options)

class GSettingsSwitchTweak(_GSettingsTweak):
    def __init__(self, schema_name, key_name, **options):
        _GSettingsTweak.__init__(self, schema_name, key_name, **options)

        w = Gtk.Switch()
        self.settings.bind(key_name, w, "active", Gio.SettingsBindFlags.DEFAULT)
        self.widget = build_label_beside_widget(self.settings.schema_get_summary(key_name), w)
        self.widget_for_size_group = w

class GSettingsFontButtonTweak(_GSettingsTweak):
    def __init__(self, schema_name, key_name, **options):
        _GSettingsTweak.__init__(self, schema_name, key_name, **options)

        w = Gtk.FontButton()
        self.settings.bind(key_name, w, "font-name", Gio.SettingsBindFlags.DEFAULT)
        self.widget = build_label_beside_widget(self.settings.schema_get_summary(key_name), w)
        self.widget_for_size_group = w

class GSettingsRangeTweak(_GSettingsTweak):
    def __init__(self, schema_name, key_name, **options):
        _GSettingsTweak.__init__(self, schema_name, key_name, **options)

        #returned variant is range:(min, max)
        _min, _max = self.settings.get_range(key_name)[1]

        w = Gtk.HScale.new_with_range(_min, _max, options.get('adjustment_step', 1))
        self.settings.bind(key_name, w.get_adjustment(), "value", Gio.SettingsBindFlags.DEFAULT)
        self.widget = build_label_beside_widget(self.settings.schema_get_summary(key_name), w)
        self.widget_for_size_group = w

