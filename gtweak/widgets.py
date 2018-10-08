# Copyright (c) 2011 John Stowers
# SPDX-License-Identifier: GPL-3.0+
# License-Filename: LICENSES/GPL-3.0

import logging

from gi.repository import GLib, Gtk, Gio, Pango

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
        image = Gtk.Image.new_from_icon_name(icon, Gtk.IconSize.MENU)
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
    lbl = Gtk.Label(label=txt)
    lbl.props.ellipsize = Pango.EllipsizeMode.END
    lbl.props.xalign = 0.0
    lbl.set_has_tooltip(True)
    lbl.connect("query-tooltip", show_tooltip_when_ellipsized)
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

    # For Atk, indicate that the rightmost widget, usually the switch relates to the
    # label. By convention this is true in the great majority of cases. Settings that
    # construct their own widgets will need to set this themselves
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
        _iter = store.append((val, name))
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


def build_tight_button(stock_id):
    button = Gtk.Button()
    button.set_relief(Gtk.ReliefStyle.NONE)
    button.set_focus_on_click(False)
    button.add(Gtk.Image.new_from_stock(stock_id, Gtk.IconSize.MENU))
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


class _GSettingsTweak(Tweak):
    def __init__(self, name, schema_name, key_name, **options):
        self.schema_name = schema_name
        self.key_name = key_name
        self._extra_info = None
        if 'uid' not in options:
            options['uid'] = key_name
        try:
            self.settings = GSettingsSetting(schema_name, **options)
            Tweak.__init__(self,
                name,
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


class ListBoxTweakGroup(Gtk.ListBox, TweakGroup):
    def __init__(self, name, *tweaks, **options):
        if 'uid' not in options:
            options['uid'] = self.__class__.__name__
        if 'activatable' not in options:
            activatable = False
        else:
            activatable = options['activatable']
        Gtk.ListBox.__init__(self,
                        selection_mode=Gtk.SelectionMode.NONE,
                        name=options['uid'])
        self.get_style_context().add_class(
                        options.get('css_class', 'tweak-group'))
        self.props.margin = 20
        self.props.vexpand = False
        self.props.valign = Gtk.Align.START

        self._sg = Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL)
        self._sg.props.ignore_hidden = True

        TweakGroup.__init__(self, name, **options)

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
                row.get_style_context().add_class("tweak")
                if isinstance(t, Title):
                    row.get_style_context().add_class("title")
                row.add(t)
            row.set_activatable(activatable)
            if position is None:
                self.add(row)
            else:
                self.insert(row, position)
            if t.widget_for_size_group:
                self._sg.add_widget(t.widget_for_size_group)
            return row


class GSettingsCheckTweak(Gtk.Box, _GSettingsTweak, _DependableMixin):
    def __init__(self, name, schema_name, key_name, **options):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.HORIZONTAL)
        _GSettingsTweak.__init__(self, name, schema_name, key_name, **options)

        widget = Gtk.CheckButton.new_with_label(name)
        self.settings.bind(
                key_name,
                widget,
                "active", Gio.SettingsBindFlags.DEFAULT)
        self.add(widget)
        self.widget_for_size_group = None

        self.add_dependency_on_tweak(
                options.get("depends_on"),
                options.get("depends_how")
        )


class GSettingsSwitchTweak(Gtk.Box, _GSettingsTweak, _DependableMixin):
    def __init__(self, name, schema_name, key_name, **options):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.HORIZONTAL)
        _GSettingsTweak.__init__(self, name, schema_name, key_name, **options)

        w = Gtk.Switch()
        self.settings.bind(key_name, w, "active", Gio.SettingsBindFlags.DEFAULT)

        self.add_dependency_on_tweak(
                options.get("depends_on"),
                options.get("depends_how")
        )

        vbox1 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        vbox1.props.spacing = UI_BOX_SPACING
        lbl = Gtk.Label(label=name)
        lbl.props.ellipsize = Pango.EllipsizeMode.END
        lbl.props.xalign = 0.0
        vbox1.pack_start(lbl, True, True, 0)

        if options.get("desc"):
            description = options.get("desc")
            lbl_desc = Gtk.Label()
            lbl_desc.props.xalign = 0.0
            lbl_desc.set_line_wrap(True)
            lbl_desc.get_style_context().add_class("dim-label")
            lbl_desc.set_markup("<span size='small'>"+GLib.markup_escape_text(description)+"</span>")
            vbox1.pack_start(lbl_desc, True, True, 0)

        vbox2 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        vbox2_upper = Gtk.Box()
        vbox2_lower = Gtk.Box()
        vbox2.pack_start(vbox2_upper, True, True, 0)
        vbox2.pack_start(w, False, False, 0)
        vbox2.pack_start(vbox2_lower, True, True, 0)

        self.pack_start(vbox1, True, True, 0)
        self.pack_start(vbox2, False, False, 0)
        self.widget_for_size_group = None


class GSettingsFontButtonTweak(Gtk.Box, _GSettingsTweak, _DependableMixin):
    def __init__(self, name, schema_name, key_name, **options):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.HORIZONTAL)
        _GSettingsTweak.__init__(self, name, schema_name, key_name, **options)

        w = Gtk.FontButton()
        w.set_use_font(True)
        self.settings.bind(key_name, w, "font-name", Gio.SettingsBindFlags.DEFAULT)
        build_label_beside_widget(name, w, hbox=self)
        self.widget_for_size_group = w


class GSettingsRangeTweak(Gtk.Box, _GSettingsTweak, _DependableMixin):
    def __init__(self, name, schema_name, key_name, **options):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.HORIZONTAL)
        _GSettingsTweak.__init__(self, name, schema_name, key_name, **options)

        # returned variant is range:(min, max)
        _min, _max = self.settings.get_range(key_name)[1]

        w = Gtk.HScale.new_with_range(_min, _max, options.get('adjustment_step', 1))
        self.settings.bind(key_name, w.get_adjustment(), "value", Gio.SettingsBindFlags.DEFAULT)

        build_label_beside_widget(self.name, w, hbox=self)
        self.widget_for_size_group = w


class GSettingsSpinButtonTweak(Gtk.Box, _GSettingsTweak, _DependableMixin):
    def __init__(self, name, schema_name, key_name, **options):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.HORIZONTAL)
        _GSettingsTweak.__init__(self, name, schema_name, key_name, **options)

        # returned variant is range:(min, max)
        _min, _max = self.settings.get_range(key_name)[1]

        adjustment = Gtk.Adjustment(value=0, lower=_min, upper=_max, step_increment=options.get('adjustment_step', 1))
        w = Gtk.SpinButton()
        w.set_adjustment(adjustment)
        w.set_digits(options.get('digits', 0))
        self.settings.bind(key_name, adjustment, "value", Gio.SettingsBindFlags.DEFAULT)

        build_label_beside_widget(name, w, hbox=self)
        self.widget_for_size_group = w

        self.add_dependency_on_tweak(
                options.get("depends_on"),
                options.get("depends_how")
        )


class GSettingsComboEnumTweak(Gtk.Box, _GSettingsTweak, _DependableMixin):
    def __init__(self, name, schema_name, key_name, **options):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.HORIZONTAL)
        _GSettingsTweak.__init__(self, name, schema_name, key_name, **options)

        _type, values = self.settings.get_range(key_name)
        value = self.settings.get_string(key_name)
        self.settings.connect('changed::'+self.key_name, self._on_setting_changed)

        w = build_combo_box_text(value, *[(v, v.replace("-", " ").title()) for v in values])
        w.connect('changed', self._on_combo_changed)
        self.combo = w

        build_label_beside_widget(name, w, hbox=self)
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
    def __init__(self, name, schema_name, key_name, key_options, **options):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.HORIZONTAL)
        _GSettingsTweak.__init__(self, name, schema_name, key_name, **options)

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

        build_label_beside_widget(name, self.combo, hbox=self)
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


class FileChooserButton(Gtk.FileChooserButton):
    def __init__(self, title, local_only, mimetypes):
        Gtk.FileChooserButton.__init__(self, title=title)

        if mimetypes:
            f = Gtk.FileFilter()
            for m in mimetypes:
                f.add_mime_type(m)
            self.set_filter(f)

        # self.set_width_chars(15)
        self.set_local_only(local_only)
        self.set_action(Gtk.FileChooserAction.OPEN)


class GSettingsFileChooserButtonTweak(Gtk.Box, _GSettingsTweak, _DependableMixin):
    def __init__(self, name, schema_name, key_name, local_only, mimetypes, **options):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.HORIZONTAL)
        _GSettingsTweak.__init__(self, name, schema_name, key_name, **options)

        self.settings.connect('changed::'+self.key_name, self._on_setting_changed)

        self.filechooser = FileChooserButton(name, local_only, mimetypes)
        self.filechooser.set_uri(self.settings.get_string(self.key_name))
        self.filechooser.connect("file-set", self._on_file_set)

        build_label_beside_widget(name, self.filechooser, hbox=self)
        self.widget_for_size_group = self.filechooser

    def _values_are_different(self):
        return self.settings.get_string(self.key_name) != self.filechooser.get_uri()

    def _on_setting_changed(self, setting, key):
        self.filechooser.set_uri(self.settings.get_string(key))

    def _on_file_set(self, chooser):
        uri = self.filechooser.get_uri()
        if uri and self._values_are_different():
            self.settings.set_string(self.key_name, uri)


class GetterSetterSwitchTweak(Gtk.Box, Tweak):
    def __init__(self, name, **options):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.HORIZONTAL)
        Tweak.__init__(self, name, options.get("description", ""), **options)

        sw = Gtk.Switch()
        sw.set_active(self.get_active())
        sw.connect("notify::active", self._on_toggled)

        build_label_beside_widget(name, sw, hbox=self)

    def _on_toggled(self, sw, pspec):
        self.set_active(sw.get_active())

    def get_active(self):
        raise NotImplementedError()

    def set_active(self, v):
        raise NotImplementedError()


class Title(Gtk.Box, Tweak):
    def __init__(self, name, desc, **options):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.HORIZONTAL)
        Tweak.__init__(self, name, desc, **options)
        widget = Gtk.Label()
        widget.set_markup("<b>"+GLib.markup_escape_text(name)+"</b>")
        widget.props.xalign = 0.0
        if not options.get("top"):
            widget.set_margin_top(10)
        self.add(widget)


class GSettingsSwitchTweakValue(Gtk.Box, _GSettingsTweak):

    def __init__(self, name, schema_name, key_name, **options):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.HORIZONTAL)
        _GSettingsTweak.__init__(self, name, schema_name, key_name, **options)

        sw = Gtk.Switch()
        sw.set_active(self.get_active())
        sw.connect("notify::active", self._on_toggled)

        vbox1 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        vbox1.props.spacing = UI_BOX_SPACING
        lbl = Gtk.Label(label=name)
        lbl.props.ellipsize = Pango.EllipsizeMode.END
        lbl.props.xalign = 0.0
        vbox1.pack_start(lbl, True, True, 0)

        if options.get("desc"):
            description = options.get("desc")
            lbl_desc = Gtk.Label()
            lbl_desc.props.xalign = 0.0
            lbl_desc.set_line_wrap(True)
            lbl_desc.get_style_context().add_class("dim-label")
            lbl_desc.set_markup("<span size='small'>"+GLib.markup_escape_text(description)+"</span>")
            vbox1.pack_start(lbl_desc, True, True, 0)

        vbox2 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        vbox2_upper = Gtk.Box()
        vbox2_lower = Gtk.Box()
        vbox2.pack_start(vbox2_upper, True, True, 0)
        vbox2.pack_start(sw, False, False, 0)
        vbox2.pack_start(vbox2_lower, True, True, 0)

        self.pack_start(vbox1, True, True, 0)
        self.pack_start(vbox2, False, False, 0)
        self.widget_for_size_group = None

    def _on_toggled(self, sw, pspec):
        self.set_active(sw.get_active())

    def set_active(self, v):
        raise NotImplementedError()

    def get_active(self):
        raise NotImplementedError()
