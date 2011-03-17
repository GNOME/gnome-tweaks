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
        self.schema_name = schema_name
        self.key_name = key_name
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

class GSettingsComboEnumTweak(_GSettingsTweak):
    def __init__(self, schema_name, key_name, **options):
        _GSettingsTweak.__init__(self, schema_name, key_name, **options)

        _type, values = self.settings.get_range(key_name)
        value = self.settings.get_string(key_name)
        self.settings.connect('changed::'+self.key_name, self._on_setting_changed)

        w = build_combo_box_text(value, *[(v,v) for v in values])
        w.connect('changed', self._on_combo_changed)
        self.combo = w

        self.widget = build_label_beside_widget(self.settings.schema_get_summary(key_name), w)
        self.widget_for_size_group = w


    def _values_are_different(self):
        #to stop bouncing back and forth between changed signals. I suspect there must be a nicer
        #Gio.settings_bind way to fix this
        return self.settings.get_string(self.key_name) != \
               self.combo.get_model().get_value(self.combo.get_active_iter(), 0)

    def _on_setting_changed(self, setting, key):
        assert key == self.key_name
        val = self.settings.get_string(key)
        model = self.combo.get_model()
        for row in model:
            if val == row[0]:
                self.combo.set_active_iter(row.iter) #iter_ = self.combo.get_model().get_iter(row)
                break

    def _on_combo_changed(self, combo):
        val = self.combo.get_model().get_value(self.combo.get_active_iter(), 0)
        if self._values_are_different():
            self.settings.set_value(self.key_name, val)

