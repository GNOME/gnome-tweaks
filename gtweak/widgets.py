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


def build_combo_box_text(selected, *values) -> Gtk.ComboBox:
    """
    builds a GtkComboBox and model containing the supplied values.
    @values: a list of 2-tuples (value, name)
    """
    store = Gtk.ListStore(str, str)
    store.set_sort_column_id(0, Gtk.SortType.ASCENDING)

    selected_iter = None
    for (val, name) in values:
        _iter = store.append([val, name])
        if val == selected:
            selected_iter = _iter

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

class ListBoxTweakGroup(Gtk.ListBox, TweakGroup):
    def __init__(self, name, title, *tweaks, **options):
        if 'uid' not in options:
            options['uid'] = self.__class__.__name__
        if 'activatable' not in options:
            activatable = False
        else:
            activatable = options['activatable']
        Gtk.ListBox.__init__(self,
                        selection_mode=Gtk.SelectionMode.NONE,
                        name=options['uid'])
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
            self.add_tweak_row(t, activatable)

    # FIXME: need to add remove_tweak_row and remove_tweak (which clears
    # the search cache etc)

    def add_tweak_row(self, t, activatable=False, position=None):
        if self.add_tweak(t):
            if isinstance(t, Gtk.ListBoxRow):
                row = t
            else:
                row = Gtk.ListBoxRow(name=t.uid)
                row.add_css_class("tweak")
                if isinstance(t, Title):
                    row.add_css_class("title")
                row.set_child(t)
            row.set_activatable(activatable)
            if position is None:
                self.append(row)
            else:
                self.insert(row, position)
            if t.widget_for_size_group:
                self._sg.add_widget(t.widget_for_size_group)
            return row


class GSettingsCheckTweak(Gtk.Box, _GSettingsTweak, _DependableMixin):
    def __init__(self, name, title, schema_name, key_name, **options):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.HORIZONTAL)
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


class GSettingsSwitchTweak(Gtk.Box, _GSettingsTweak, _DependableMixin):
    def __init__(self, title: str, schema_name: str, key_name: str, **options):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.HORIZONTAL,
                         margin_top=UI_BOX_SPACING, margin_bottom=UI_BOX_SPACING)
        _GSettingsTweak.__init__(self, title, schema_name, key_name, **options)

        switch = Gtk.Switch(halign=Gtk.Align.CENTER,
                            valign=Gtk.Align.CENTER)
        self.settings.bind(key_name, switch, "active", Gio.SettingsBindFlags.DEFAULT)

        self.add_dependency_on_tweak(
            options.get("depends_on"),
            options.get("depends_how")
        )

        vbox1 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,
                        hexpand=True,
                        valign=Gtk.Align.CENTER)
        vbox1.props.spacing = UI_BOX_SPACING
        lbl = Gtk.Label(label=title, xalign=0.0)
        lbl.props.ellipsize = Pango.EllipsizeMode.NONE
        lbl.props.xalign = 0.0
        vbox1.append(lbl)

        if options.get("desc"):
            description = options.get("desc")
            lbl_desc = Gtk.Label(xalign=0.0, wrap=True)
            lbl_desc.add_css_class("dim-label")
            lbl_desc.set_markup(
                "<span size='small'>" + GLib.markup_escape_text(description) + "</span>")
            vbox1.append(lbl_desc)

        self.append(vbox1)
        self.append(switch)
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


class GSettingsSpinButtonTweak(Gtk.Box, _GSettingsTweak, _DependableMixin):
    def __init__(self, title, schema_name, key_name, **options):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.HORIZONTAL)
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


class GSettingsComboEnumTweak(Gtk.Box, _GSettingsTweak, _DependableMixin):
    def __init__(self, title, schema_name, key_name, **options):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.HORIZONTAL)
        _GSettingsTweak.__init__(self, title, schema_name, key_name, **options)

        _type, values = self.settings.get_range(key_name)
        value = self.settings.get_string(key_name)
        self.settings.connect('changed::'+self.key_name, self._on_setting_changed)

        w = build_combo_box_text(value, *[(v, v.replace("-", " ").title()) for v in values])
        w.connect('changed', self._on_combo_changed)
        self.combo = w

        build_label_beside_widget(title, w, hbox=self)
        self.widget_for_size_group = w

    def _values_are_different(self):
        # to stop bouncing back and forth between changed signals. I suspect there must be a nicer
        # Gio.settings_bind way to fix this
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


class GSettingsComboTweak(Gtk.Box, _GSettingsTweak, _DependableMixin):
    def __init__(self, title, schema_name, key_name, key_options, **options):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.HORIZONTAL)
        _GSettingsTweak.__init__(self, title, schema_name, key_name, **options)

        # check key_options is iterable
        # and if supplied, check it is a list of 2-tuples
        assert len(key_options) >= 0
        if len(key_options):
            assert len(key_options[0]) == 2
        self._key_options = key_options

        self.combo = build_combo_box_text(
                    self.settings.get_string(self.key_name),
                    *key_options)
        self.combo.connect('changed', self._on_combo_changed)
        self.settings.connect('changed::'+self.key_name, self._on_setting_changed)

        build_label_beside_widget(title, self.combo, hbox=self)
        self.widget_for_size_group = self.combo

    def _on_setting_changed(self, setting, key):
        assert key == self.key_name
        val = self.settings.get_string(key)
        model = self.combo.get_model()
        for row in model:
            if val == row[0]:
                self.combo.set_active_iter(row.iter)
                return

        self.combo.set_active(-1)

    def _on_combo_changed(self, combo):
        _iter = combo.get_active_iter()
        if _iter:
            value = combo.get_model().get_value(_iter, 0)
            self.settings.set_string(self.key_name, value)

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


class Title(Gtk.Box, Tweak):
    def __init__(self, name,  desc, **options):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.HORIZONTAL)
        Tweak.__init__(self, name, desc, **options)
        widget = Gtk.Label()
        widget.set_markup("<b>"+GLib.markup_escape_text(name)+"</b>")
        widget.props.xalign = 0.0
        if not options.get("top"):
            widget.set_margin_top(10)
        self.append(widget)


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
