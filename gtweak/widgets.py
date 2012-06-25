# This file is part of gnome-tweak-tool.
#
# Copyright (c) 2011 John Stowers
#
# gnome-tweak-tool is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# gnome-tweak-tool is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with gnome-tweak-tool.  If not, see <http://www.gnu.org/licenses/>.

import logging

from gi.repository import Gtk, Gdk, Gio, Pango

from gtweak.tweakmodel import Tweak
from gtweak.gsettings import GSettingsSetting, GSettingsFakeSetting, GSettingsMissingError
from gtweak.gconf import GConfSetting

def build_label_beside_widget(txt, *widget, **kwargs):
    """
    Builds a HBox containing widgets.

    Optional Kwargs:
        hbox: Use an existing HBox, not a new one
        info: Informational text to be shown after the label
        warning: Warning text to be shown after the label
    """
    def make_image(icon, tip):
        image = Gtk.Image.new_from_icon_name(icon, Gtk.IconSize.MENU)
        image.set_tooltip_text(tip)
        return image

    if kwargs.get("hbox"):
        hbox = kwargs.get("hbox")
    else:
        hbox = Gtk.HBox()

    hbox.props.spacing = 4
    lbl = Gtk.Label(txt)
    lbl.props.ellipsize = Pango.EllipsizeMode.END
    lbl.props.xalign = 0.0
    hbox.pack_start(lbl, True, True, 0)

    if kwargs.get("info"):
        hbox.pack_start(
                make_image("dialog-information-symbolic", kwargs.get("info")),
                False, False, 0)
    if kwargs.get("warning"):
        hbox.pack_start(
                make_image("dialog-warning-symbolic", kwargs.get("warning")),
                False, False, 0)

    for w in widget:
        hbox.pack_start(w, False, False, 0)

    #For Atk, indicate that the rightmost widget, usually the switch relates to the
    #label. By convention this is true in the great majority of cases. Settings that
    #construct their own widgets will need to set this themselves
    lbl.set_mnemonic_widget(widget[-1])

    return hbox

def build_combo_box_text(selected, *values):
    """
    builds a GtkComboBox and model containing the supplied values.
    @values: a list of 2-tuples (value, name)
    """
    store = Gtk.ListStore(str, str)
    store.set_sort_column_id(0, Gtk.SortType.ASCENDING)

    selected_iter = None
    for (val, name) in values:
        _iter = store.append( (val, name) )
        if val == selected:
            selected_iter = _iter

    combo = Gtk.ComboBox(model=store)
    renderer = Gtk.CellRendererText()
    combo.pack_start(renderer, True)
    combo.add_attribute(renderer, 'markup', 1)
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
        try:
            self.settings = GSettingsSetting(schema_name, **options)
            Tweak.__init__(self,
                options.get("summary",self.settings.schema_get_summary(key_name)),
                options.get("description",self.settings.schema_get_description(key_name)),
                **options)
        except GSettingsMissingError, e:
            self.settings = GSettingsFakeSetting()
            Tweak.__init__(self,"","")
            self.loaded = False
            logging.info("Missing gsettings %s" % (e.message))
        except KeyError:
            self.settings = GSettingsFakeSetting()
            Tweak.__init__(self,"","")
            self.loaded = False
            logging.info("Missing gsettings %s (key %s)" % (schema_name, key_name))


class GSettingsSwitchTweak(_GSettingsTweak):
    def __init__(self, schema_name, key_name, **options):
        _GSettingsTweak.__init__(self, schema_name, key_name, **options)

        w = Gtk.Switch()
        self.settings.bind(key_name, w, "active", Gio.SettingsBindFlags.DEFAULT)
        self.widget = build_label_beside_widget(self.name, w)
        # never change the size of a switch
        self.widget_for_size_group = None

class GSettingsFontButtonTweak(_GSettingsTweak):
    def __init__(self, schema_name, key_name, **options):
        _GSettingsTweak.__init__(self, schema_name, key_name, **options)

        w = Gtk.FontButton()
        self.settings.bind(key_name, w, "font-name", Gio.SettingsBindFlags.DEFAULT)
        self.widget = build_label_beside_widget(self.name, w)
        self.widget_for_size_group = w

class GSettingsRangeTweak(_GSettingsTweak):
    def __init__(self, schema_name, key_name, **options):
        _GSettingsTweak.__init__(self, schema_name, key_name, **options)

        #returned variant is range:(min, max)
        _min, _max = self.settings.get_range(key_name)[1]

        w = Gtk.HScale.new_with_range(_min, _max, options.get('adjustment_step', 1))
        self.settings.bind(key_name, w.get_adjustment(), "value", Gio.SettingsBindFlags.DEFAULT)
        self.widget = build_label_beside_widget(self.name, w)
        self.widget_for_size_group = w

class GSettingsSpinButtonTweak(_GSettingsTweak):
    def __init__(self, schema_name, key_name, **options):
        _GSettingsTweak.__init__(self, schema_name, key_name, **options)

        #returned variant is range:(min, max)
        _min, _max = self.settings.get_range(key_name)[1]

        adjustment = Gtk.Adjustment(0, _min, _max, options.get('adjustment_step', 1))
        w = Gtk.SpinButton()
        w.set_adjustment(adjustment)
        w.set_digits(options.get('digits', 0))
        self.settings.bind(key_name, adjustment, "value", Gio.SettingsBindFlags.DEFAULT)
        self.widget = build_label_beside_widget(self.name, w)
        self.widget_for_size_group = w

class GSettingsComboEnumTweak(_GSettingsTweak):
    def __init__(self, schema_name, key_name, **options):
        _GSettingsTweak.__init__(self, schema_name, key_name, **options)

        _type, values = self.settings.get_range(key_name)
        value = self.settings.get_string(key_name)
        self.settings.connect('changed::'+self.key_name, self._on_setting_changed)

        w = build_combo_box_text(value, *[(v,v.replace("-"," ").title()) for v in values])
        w.connect('changed', self._on_combo_changed)
        self.combo = w

        self.widget = build_label_beside_widget(self.name, w)
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
                self.combo.set_active_iter(row.iter)
                break

    def _on_combo_changed(self, combo):
        val = self.combo.get_model().get_value(self.combo.get_active_iter(), 0)
        if self._values_are_different():
            self.settings.set_string(self.key_name, val)

class GSettingsComboTweak(_GSettingsTweak):
    def __init__(self, schema_name, key_name, key_options, **options):
        _GSettingsTweak.__init__(self, schema_name, key_name, **options)

        #check key_options is iterable
        #and if supplied, check it is a list of 2-tuples
        assert len(key_options) >= 0
        if len(key_options):
            assert len(key_options[0]) == 2

        combo = build_combo_box_text(
                    self.settings.get_string(self.key_name),
                    *key_options)
        combo.connect('changed', self._on_combo_changed)
        self.widget = build_label_beside_widget(self.name, combo)
        self.widget_for_size_group = combo

    def _on_combo_changed(self, combo):
        _iter = combo.get_active_iter()
        if _iter:
            value = combo.get_model().get_value(_iter, 0)
            self.settings.set_string(self.key_name, value)

class _GConfTweak(Tweak):
    def __init__(self, key_name, key_type, **options):
        self.gconf = GConfSetting(key_name, key_type)
        Tweak.__init__(self,
            options.get("summary",self.gconf.schema_get_summary()),
            options.get("description",self.gconf.schema_get_description()),
            **options)

class GConfComboTweak(_GConfTweak):
    def __init__(self, key_name, key_type, key_options, **options):
        _GConfTweak.__init__(self, key_name, key_type, **options)

        #check key_options is iterable
        #and if supplied, check it is a list of 2-tuples
        assert len(key_options) >= 0
        if len(key_options):
            assert len(key_options[0]) == 2

        combo = build_combo_box_text(
            self.gconf.get_value(),
            *key_options)
        combo.connect('changed', self._on_combo_changed)
        self.widget = build_label_beside_widget(self.name, combo)
        self.widget_for_size_group = combo

    def _on_combo_changed(self, combo):
        _iter = combo.get_active_iter()
        if _iter:
            value = combo.get_model().get_value(_iter, 0)
            self.gconf.set_value(value)

class GConfFontButtonTweak(_GConfTweak):
    def __init__(self, key_name, key_type, **options):
        _GConfTweak.__init__(self, key_name, key_type, **options)

        w = Gtk.FontButton()
        w.props.font_name = self.gconf.get_value()
        w.connect("notify::font-name", self._on_fontbutton_changed)
        self.widget = build_label_beside_widget(self.name, w)
        self.widget_for_size_group = w

    def _on_fontbutton_changed(self, btn, param):
        self.gconf.set_value(btn.props.font_name)

class ZipFileChooserButton(Gtk.FileChooserButton):
    def __init__(self, title):
        Gtk.FileChooserButton.__init__(self, title=title)

        f = Gtk.FileFilter()
        f.add_mime_type("application/zip")
        self.set_filter(f)

        #self.set_width_chars(15)
        self.set_local_only(True)

