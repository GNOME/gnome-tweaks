# Copyright (c) 2011 John Stowers
# SPDX-License-Identifier: GPL-3.0+
# License-Filename: LICENSES/GPL-3.0

import logging
from typing import List

from gi.repository import Adw, GLib, Gtk, Gio, GObject, Pango

from gtweak.tweakmodel import Tweak, TweakGroup
from gtweak.gsettings import GSettingsSetting, GSettingsFakeSetting, GSettingsMissingError
from gtweak.gshellwrapper import GnomeShellFactory

UI_BOX_SPACING = 4
UI_BOX_HORIZONTAL_SPACING = 10
_shell = GnomeShellFactory().get_shell()


def build_label_beside_widget(txt, *widget, **kwargs):
    """
    Builds a HBox containing widgets.

    Optional Kwargs:
        hbox: Use an existing HBox, not a new one
        info: Informational text to be shown after the label
        warning: Warning text to be shown after the label
    """
    def make_image(icon, tip):
        image = Gtk.Image.new_from_icon_name(icon)
        image.set_tooltip_text(tip)
        return image

    def show_tooltip_when_ellipsized(label, x, y, keyboard_mode, tooltip):
        layout = label.get_layout()
        if layout.is_ellipsized():
            tooltip.set_text(label.get_text())
            return True
        else:
            return False

    if kwargs.get("hbox"):
        hbox = kwargs.get("hbox")
    else:
        hbox = Gtk.Box()

    hbox.props.spacing = UI_BOX_SPACING
    lbl = Gtk.Label(label=txt, hexpand=True)
    lbl.props.ellipsize = Pango.EllipsizeMode.END
    lbl.props.xalign = 0.0
    lbl.set_has_tooltip(True)
    lbl.connect("query-tooltip", show_tooltip_when_ellipsized)
    hbox.append(lbl)

    if kwargs.get("info"):
        hbox.append(
                make_image("dialog-information-symbolic", kwargs.get("info")))
    if kwargs.get("warning"):
        hbox.append(
                make_image("dialog-warning-symbolic", kwargs.get("warning")))

    for w in widget:
        hbox.append(w)

    # For Atk, indicate that the rightmost widget, usually the switch relates to the
    # label. By convention this is true in the great majority of cases. Settings that
    # construct their own widgets will need to set this themselves
    lbl.set_mnemonic_widget(widget[-1])

    return hbox

def build_combo_box_model(*values) -> Gio.ListModel:
    """
    builds a GtkComboBox and model containing the supplied values.
    @values: a list of 2-tuples (value, name)
    """
    store = Gtk.StringList()
    for (text,value) in values:
        store.append(text)

    return store

def build_combo_box_text_model(*values) -> Gtk.ListStore:
    """
    builds a GtkComboBox and model containing the supplied values.
    @values: a list of 2-tuples (value, name)
    """
    store = Gtk.ListStore(str, str)
    store.set_sort_column_id(0, Gtk.SortType.ASCENDING)

    for (val, name) in values:
        store.append([val, name])
    
    return store

def equal_func(a, b):
    return a == b

def build_combo_box_text(selected, *values) -> Gtk.ComboBox:
    store = build_combo_box_text_model(*values)

    selected_iter = None
    for val in values:
        if val == selected:
            selected_iter = store.find_with_equal_func(val, equal_func)

    combo = Gtk.ComboBox(model=store)
    renderer = Gtk.CellRendererCombo()
    combo.pack_start(renderer, True)
    combo.add_attribute(renderer, 'markup', 1)
    if selected_iter:
        combo.set_active_iter(selected_iter)

    return combo


def build_horizontal_sizegroup():
    sg = Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL)
    return sg


def build_tight_button(stock_id):
    button = Gtk.Button()
    button.set_has_frame(False)
    button.set_focus_on_click(False)
    button.set_child(Gtk.Image.new_from_stock(stock_id))
    data = ".button {\n" \
           "-GtkButton-default-border : 0px;\n" \
           "-GtkButton-default-outside-border : 0px;\n" \
           "-GtkButton-inner-border: 0px;\n" \
           "-GtkWidget-focus-line-width : 0px;\n" \
           "-GtkWidget-focus-padding : 0px;\n" \
           "padding: 0px;\n" \
           "}"
    provider = Gtk.CssProvider()
    provider.load_from_data(data)
    # 600 = GTK_STYLE_PROVIDER_PRIORITY_APPLICATION
    button.get_style_context().add_provider(provider, 600)
    return button


class TickActionRow(Adw.ActionRow):

    def __init__(self, title: str, subtitle: str, keyvalue: str):
        super().__init__()
        self.set_title(title)
        self.set_subtitle(subtitle)

        self.keyvalue = keyvalue
        self.img = Gtk.Image.new_from_icon_name("object-select-symbolic")

        self.add_suffix(self.img)
        self.set_activatable_widget(self.img)


class _GSettingsTweak(Tweak):
    def __init__(self, title, schema_name, key_name, **options):
        self.schema_name = schema_name
        self.key_name = key_name
        self._extra_info = None
        if 'uid' not in options:
            options['uid'] = key_name
        try:
            self.settings = GSettingsSetting(schema_name, **options)
            Tweak.__init__(self,
                title,
                options.get("description",self.settings.schema_get_description(key_name)),
                **options)
        except GSettingsMissingError as e:
            self.settings = GSettingsFakeSetting()
            Tweak.__init__(self, "", "")
            self.loaded = False
            logging.info("GSetting missing %s", e)
        except KeyError:
            self.settings = GSettingsFakeSetting()
            Tweak.__init__(self, "", "")
            self.loaded = False
            logging.info("GSettings missing key %s (key %s)" % (schema_name, key_name))

        if options.get("logout_required") and self.loaded:
            self.settings.connect("changed::%s" % key_name, self._on_changed_notify_logout)

    def _on_changed_notify_logout(self, settings, key_name):
        self.notify_logout()

    @property
    def extra_info(self):
        if self._extra_info is None:
            self._extra_info = self.settings.schema_get_summary(self.key_name)
        return self._extra_info


class _DependableMixin(object):

    def add_dependency_on_tweak(self, depends, depends_how):
        if isinstance(depends, Tweak):
            self._depends = depends
            if depends_how is None:
                depends_how = lambda x, kn: x.get_boolean(kn)
            self._depends_how = depends_how

            sensitive = self._depends_how(
                                depends.settings,
                                depends.key_name,
            )
            self.set_sensitive(sensitive)

            depends.settings.connect("changed::%s" % depends.key_name, self._on_changed_depend)

    def _on_changed_depend(self, settings, key_name):
        sensitive = self._depends_how(settings, key_name)
        self.set_sensitive(sensitive)

class TweakListBoxRow(Gtk.ListBoxRow):
    __gtype_name__ = "GTweakListBoxRow"

    tweakname = GObject.Property(type=str)

from typing import Union

class ListBoxTweakGroup(Gtk.Box, TweakGroup):
    def __init__(self, name, title, *tweaks: Union[Tweak, "ListBoxTweakSubgroup"], **options):
        if 'uid' not in options:
            options['uid'] = self.__class__.__name__
        Gtk.Box.__init__(self,
                        name=options['uid'],
                        spacing=10,
                        orientation=Gtk.Orientation.VERTICAL)
        self.add_css_class(options.get('css_class', 'tweak-group'))
        self.set_margin_top(20)
        self.set_margin_bottom(20)
        self.set_margin_start(20)
        self.set_margin_end(20)
        self.props.vexpand = False
        self.props.valign = Gtk.Align.START
        self.props.hexpand = True
        self.props.halign = Gtk.Align.FILL

        self._sg = Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL)

        TweakGroup.__init__(self, name, title, **options)

        for t in tweaks:
            if isinstance(t, ListBoxTweakSubgroup):
                for st in t.tweaks:
                    self.add_tweak(st)
                self.append(t)
            else:
                self.add_tweak_row(t)

    # FIXME: need to add remove_tweak_row and remove_tweak (which clears
    # the search cache etc)

    def add_tweak_row(self, t):
        if self.add_tweak(t):
            row = t

            self.append(row)

            if t.widget_for_size_group:
                self._sg.add_widget(t.widget_for_size_group)
            return row

from typing import Tuple

class ListBoxTweakSubgroup(Adw.PreferencesGroup, TweakGroup):
    def __init__(self, title, name, *tweaks: Tweak):
        Adw.PreferencesGroup.__init__(self)
        TweakGroup.__init__(self, name, title)

        self.set_title(title)

        self._sg = Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL)

        for t in tweaks:
            self.add_tweak_row(t)


    def add_tweak_row(self, t: Tweak):
        if self.add_tweak(t):
            if isinstance(t, Adw.PreferencesRow):
                self.add(t)
            else:
                row = Adw.PreferencesRow()
                row.add_css_class("tweak-row")
                row.set_title(t.title)
                row.set_child(t)

                self.add(row)

            if t.widget_for_size_group:
                self._sg.add_widget(t.widget_for_size_group)

class GSettingsCheckTweak(Gtk.Box, _GSettingsTweak, _DependableMixin):
    def __init__(self, name, title, schema_name, key_name, **options):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.HORIZONTAL,  margin_start=UI_BOX_HORIZONTAL_SPACING, margin_end=UI_BOX_HORIZONTAL_SPACING, margin_top=UI_BOX_SPACING, margin_bottom=UI_BOX_SPACING)
        _GSettingsTweak.__init__(self, title, schema_name, key_name, **options)

        widget = Gtk.CheckButton.new_with_label(name)
        self.settings.bind(
                key_name,
                widget,
                "active", Gio.SettingsBindFlags.DEFAULT)
        self.append(widget)
        self.widget_for_size_group = None

        self.add_dependency_on_tweak(
                options.get("depends_on"),
                options.get("depends_how")
        )


class GSettingsSwitchTweak(Adw.ActionRow, _GSettingsTweak, _DependableMixin):
    def __init__(self, title: str, schema_name: str, key_name: str, **options):
        Adw.ActionRow.__init__(self, title=title)
        _GSettingsTweak.__init__(self, title, schema_name, key_name, **options)

        switch = Gtk.Switch(halign=Gtk.Align.CENTER,
                            valign=Gtk.Align.CENTER)
        self.settings.bind(key_name, switch, "active", Gio.SettingsBindFlags.DEFAULT)

        self.add_dependency_on_tweak(
            options.get("depends_on"),
            options.get("depends_how")
        )

        description = options.get("desc", None)
        if description:
            self.set_subtitle(description)

        self.add_suffix(switch)
        self.set_activatable_widget(switch)
        self.widget_for_size_group = None


class GSettingsFontButtonTweak(Gtk.Box, _GSettingsTweak, _DependableMixin):
    def __init__(self, title, schema_name, key_name, **options):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.HORIZONTAL)
        _GSettingsTweak.__init__(self, title, schema_name, key_name, **options)

        w = Gtk.FontButton()
        w.set_use_font(True)
        self.settings.bind(key_name, w, "font", Gio.SettingsBindFlags.DEFAULT)
        build_label_beside_widget(title, w, hbox=self)
        self.widget_for_size_group = w


class GSettingsRangeTweak(Gtk.Box, _GSettingsTweak, _DependableMixin):
    def __init__(self, title, schema_name, key_name, **options):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.HORIZONTAL)
        _GSettingsTweak.__init__(self, title, schema_name, key_name, **options)

        # returned variant is range:(min, max)
        _min, _max = self.settings.get_range(key_name)[1]

        w = Gtk.HScale.new_with_range(_min, _max, options.get('adjustment_step', 1))
        self.settings.bind(key_name, w.get_adjustment(), "value", Gio.SettingsBindFlags.DEFAULT)

        build_label_beside_widget(self.title, w, hbox=self)
        self.widget_for_size_group = w

# TODO: Port to AdwSpinRow
class GSettingsSpinButtonTweak(Gtk.Box, _GSettingsTweak, _DependableMixin):
    def __init__(self, title, schema_name, key_name, **options):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.HORIZONTAL, margin_start=UI_BOX_HORIZONTAL_SPACING, margin_end=UI_BOX_HORIZONTAL_SPACING, margin_top=UI_BOX_SPACING, margin_bottom=UI_BOX_SPACING)
        _GSettingsTweak.__init__(self, title, schema_name, key_name, **options)

        # returned variant is range:(min, max)
        _min, _max = self.settings.get_range(key_name)[1]

        adjustment = Gtk.Adjustment(value=0, lower=_min, upper=_max, step_increment=options.get('adjustment_step', 1))
        w = Gtk.SpinButton()
        w.set_adjustment(adjustment)
        w.set_digits(options.get('digits', 0))
        self.settings.bind(key_name, adjustment, "value", Gio.SettingsBindFlags.DEFAULT)

        build_label_beside_widget(title, w, hbox=self)
        self.widget_for_size_group = w

        self.add_dependency_on_tweak(
                options.get("depends_on"),
                options.get("depends_how")
        )

class TweakListStoreItem(GObject.Object):
    _title = ''
    _value = ''
    
    @GObject.Property(type=GObject.TYPE_STRING)
    def title(self):
        return self._title

    @title.setter
    def _set_title(self, title: str):
        self._title = title

    @GObject.Property(type=GObject.TYPE_STRING)
    def value(self):
        return self._value
    
    @value.setter
    def _set_value(self, value: str):
        self._value = value

def build_list_store(values):
    options = [TweakListStoreItem(value=value, title=title) for (value, title) in values]
    store = Gio.ListStore()
    
    for option in options:
        store.append(option)
    
    return store

def build_gsettings_list_store(values):
    options = [TweakListStoreItem(value=v, title=v.replace("-", " ").title()) for v in values]
    store = Gio.ListStore()
    
    for option in options:
        store.append(option)
    
    return store

class GSettingsComboEnumTweak(Adw.ComboRow, _GSettingsTweak, _DependableMixin):
    def __init__(self, title, schema_name, key_name, **options):
        Adw.ComboRow.__init__(self, title=title)
        _GSettingsTweak.__init__(self, title, schema_name, key_name, **options)

        _, values = self.settings.get_range(key_name)

        self.set_model(build_gsettings_list_store(values))
        self.set_expression(Gtk.PropertyExpression.new(TweakListStoreItem, None, "title"))

        self.connect('notify::selected-item', self._on_combo_changed)
        self.settings.connect('changed::' + self.key_name, self._on_setting_changed)

        self._on_setting_changed({}, self.key_name)

        self.widget_for_size_group = self

    def _on_setting_changed(self, setting, key):
        assert key == self.key_name
        val = self.settings.get_string(key)
        model = self.get_model()
        index = next((i for (i, item) in enumerate(model) if item.value == val), -1)
        if index > 0 and self.get_selected() != index:
            self.set_selected(index)

    def _on_combo_changed(self, combo, _):
        item = combo.get_selected_item()

        if item:
            self.settings.set_string(self.key_name, item.value)


class GSettingsComboTweak(Adw.ComboRow, _GSettingsTweak, _DependableMixin):
    def __init__(self, title, schema_name, key_name, key_options, **options):
        _GSettingsTweak.__init__(self, title, schema_name, key_name, **options)
        Adw.ComboRow.__init__(self, title=title)

        # check key_options is iterable
        # and if supplied, check it is a list of 2-tuples
        assert len(key_options) >= 0
        if len(key_options):
            assert len(key_options[0]) == 2
        self._key_options = key_options

        self.set_model(build_list_store(key_options))

        self.settings.connect('changed::'+self.key_name, self._on_setting_changed)
        self._update_combo_for_setting()

        self.set_expression(Gtk.PropertyExpression.new(TweakListStoreItem, None, "title"))
        self.connect('notify::selected-item', self._on_combo_changed)

        self.widget_for_size_group = self

    def _update_combo_for_setting(self):
        val = self.settings.get_string(self.key_name)
        model = self.get_model()
        index = next((i for (i, item) in enumerate(model) if item.value == val), None)
        if index is not None:
            self.set_selected(index)

    def _on_setting_changed(self, _, key):
        assert key == self.key_name

        self._update_combo_for_setting()

    def _on_combo_changed(self, combo, _):
        item = combo.get_selected_item()

        if item:
          self.settings.set_string(self.key_name, item.value)

    @property
    def extra_info(self):
        if self._extra_info is None:
            self._extra_info = self.settings.schema_get_summary(self.key_name)
            self._extra_info += " " + " ".join(op[0] for op in self._key_options)
        return self._extra_info


class FileChooserButton(Gtk.Button, GObject.Object):
    """
    An Implementation of the deprecated filechooser button for GTK4
    """

    def __init__(self, title, mimetypes: List[str]):
        super().__init__()
        self._btn_content = Adw.ButtonContent(label=_("None"),
                                              icon_name="document-open-symbolic")
        self.set_child(self._btn_content)

        self._mimetypes = mimetypes
        self._title = title
        self._file = None

        self.connect("clicked", self._on_clicked)
        self.connect("realize", self._on_realize)

    def _on_realize(self, _user_data):
        if self._file:
            self._btn_content.set_label(self._file.get_basename())

    @GObject.Property(str)
    def file_uri(self) -> str:
        return self._file.get_uri()

    @file_uri.setter
    def _set_file_uri(self, uri: str):
        self._file = Gio.File.new_for_uri(uri)

        if self.get_realized():
            self._btn_content.set_label(self._file.get_basename())

    def _on_clicked(self, _: Gtk.Button):
        mimetypes = self._mimetypes
        title = self._title

        file_chooser = Gtk.FileDialog(title=title)

        if mimetypes:
            filter = Gtk.FileFilter()
            for mime in mimetypes:
                filter.add_mime_type(mime)
            store = Gio.ListStore(item_type=Gtk.FileFilter)
            store.append(filter)
            file_chooser.set_filters(store)

        main_app = Gtk.Application.get_default()
        main_app.mark_busy()

        file_chooser.open(main_app.get_active_window(), None, self._on_response, None)

    def _on_response(self, file_dialog: Gtk.FileDialog, result, _user_data):
        main_app = Gtk.Application.get_default()
        file = file_dialog.open_finish(result)
        if file:
            self.props.file_uri = file.get_uri()

        main_app.unmark_busy()

    @GObject.Signal()
    def file_set(self):
        pass


class GSettingsFileChooserButtonTweak(Gtk.Box, _GSettingsTweak, _DependableMixin):
    def __init__(self, title, schema_name, key_name, mimetypes, **options):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.HORIZONTAL)
        _GSettingsTweak.__init__(self, title, schema_name, key_name, **options)

        self.settings.connect('changed::' + self.key_name, self._on_setting_changed)

        self.filechooser = FileChooserButton(title, mimetypes)
        self.filechooser.props.file_uri = self.settings.get_string(self.key_name)
        self.filechooser.connect("notify::file-uri", self._on_file_set)

        build_label_beside_widget(title, self.filechooser, hbox=self)
        self.widget_for_size_group = self.filechooser

    def _values_are_different(self):
        return self.settings.get_string(self.key_name) != self.filechooser.props.file_uri

    def _on_setting_changed(self, setting: GSettingsSetting, key):
        self.filechooser.props.file_uri = setting.get_string(key)

    def _on_file_set(self, filechooser: FileChooserButton, _):
        uri = filechooser.props.file_uri
        if uri and self._values_are_different():
            self.settings.set_string(self.key_name, uri)


class GetterSetterSwitchTweak(Gtk.Box, Tweak):
    def __init__(self, title, **options):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.HORIZONTAL)
        Tweak.__init__(self, title, options.get("description", ""), **options)

        sw = Gtk.Switch()
        sw.set_active(self.get_active())
        sw.connect("notify::active", self._on_toggled)

        build_label_beside_widget(title, sw, hbox=self)

    def _on_toggled(self, sw, pspec):
        self.set_active(sw.get_active())

    def get_active(self):
        raise NotImplementedError()

    def set_active(self, v):
        raise NotImplementedError()

class GSettingsSwitchTweakValue(Gtk.Box, _GSettingsTweak):

    def __init__(self, title, schema_name, key_name, **options):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.HORIZONTAL,
                         margin_top = UI_BOX_SPACING, margin_bottom = UI_BOX_SPACING)
        _GSettingsTweak.__init__(self, title, schema_name, key_name, **options)

        sw = Gtk.Switch(halign=Gtk.Align.CENTER,
                        valign=Gtk.Align.CENTER)
        sw.set_active(self.get_active())
        sw.connect("notify::active", self._on_toggled)

        vbox1 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,
                        hexpand=True,
                        valign=Gtk.Align.CENTER)
        vbox1.props.spacing = UI_BOX_SPACING
        lbl = Gtk.Label(label=title)
        lbl.props.ellipsize = Pango.EllipsizeMode.NONE
        lbl.props.xalign = 0.0
        vbox1.append(lbl)

        if options.get("desc"):
            description = options.get("desc")
            lbl_desc = Gtk.Label()
            lbl_desc.props.xalign = 0.0
            lbl_desc.set_wrap(True)
            lbl_desc.add_css_class("dim-label")
            lbl_desc.set_markup(
                "<span size='small'>" + GLib.markup_escape_text(description) + "</span>")
            vbox1.append(lbl_desc)

        self.append(vbox1)
        self.append(sw)
        self.widget_for_size_group = None

    def _on_toggled(self, sw, pspec):
        self.set_active(sw.get_active())

    def set_active(self, v):
        raise NotImplementedError()

    def get_active(self):
        raise NotImplementedError()
