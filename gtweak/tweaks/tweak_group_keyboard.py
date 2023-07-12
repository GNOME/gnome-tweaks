# Copyright (c) 2011 John Stowers
# SPDX-License-Identifier: GPL-3.0+
# License-Filename: LICENSES/GPL-3.0

import gi
gi.require_version("GnomeDesktop", "3.0")
from gi.repository import Gio, GLib, Gtk, Gdk, GnomeDesktop, Gtk

from gtweak.gshellwrapper import GnomeShellFactory
from gtweak.widgets import ListBoxTweakGroup, GSettingsSwitchTweak, GSettingsSwitchTweakValue, _GSettingsTweak, Title, build_label_beside_widget, Tweak
from gtweak.tweakmodel import Tweak, TweakGroup
from gtweak.gsettings import GSettingsSetting, GSettingsMissingError



_shell = GnomeShellFactory().get_shell()
_shell_loaded = _shell is not None


class _XkbOption(Gtk.Expander, Tweak):
    def __init__(self, group_id, parent_settings, xkb_info, **options):
        try:
            desc = xkb_info.description_for_group(group_id)
        except AttributeError:
            desc = group_id
        Gtk.Expander.__init__(self)
        Tweak.__init__(self, desc, desc, **options)

        self.set_label(self.title)
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
        vbox.set_margin_start(15)
        self.add(vbox)

        self._multiple_selection = not group_id in { 'keypad', 'kpdl', 'caps', 'altwin', 'nbsp', 'esperanto' }
        self._group_id = group_id
        self._parent_settings = parent_settings
        self._xkb_info = xkb_info
        self._possible_values = []

        model_values = []
        if not self._multiple_selection:
            model_values.append((None, _("Disabled")))

        for option_id in self._xkb_info.get_options_for_group(group_id):
            desc = self._xkb_info.description_for_option(group_id, option_id)
            model_values.append((option_id, desc))
            self._possible_values.append(option_id)

        def values_cmp_py3_wrap(f):
            ''' https://docs.python.org/3/howto/sorting.html#the-old-way-using-the-cmp-parameter '''
            class C:
                def __init__(self, obj, *args):
                    self.obj = obj
                def __lt__(self, other):
                    return f(self.obj, other.obj) < 0
                def __gt__(self, other):
                    return f(self.obj, other.obj) > 0
                def __eq__(self, other):
                    return f(self.obj, other.obj) == 0
                def __le__(self, other):
                    return f(self.obj, other.obj) <= 0
                def __ge__(self, other):
                    return f(self.obj, other.obj) >= 0
                def __ne__(self, other):
                    return f(self.obj, other.obj) != 0
            return C

        def values_cmp(xxx_todo_changeme, xxx_todo_changeme1):
            (av, ad) = xxx_todo_changeme
            (bv, bd) = xxx_todo_changeme1
            if not av:
                return -1
            elif not bv:
                return 1
            else:
                return (ad > bd) - (ad < bd)
        model_values.sort(key=values_cmp_py3_wrap(values_cmp))

        self._widgets = dict()
        for (val, name) in model_values:
            w = None
            if self._multiple_selection:
                w = Gtk.CheckButton.new()
            else:
                w = Gtk.RadioButton.new_from_widget(self._widgets.get(None))
            self._widgets[val] = w;
            vbox.add(w)
            l = Gtk.Label(label=name)
            l.set_line_wrap(True)
            w.add(l)
            w._changed_id = w.connect('toggled', self._on_toggled)
            w._val = val

        self.widget_for_size_group = None
        self.reload()

    def reload(self):
        self._values = []
        for v in self._parent_settings.get_strv(TypingTweakGroup.XKB_GSETTINGS_NAME):
            if (v in self._possible_values):
                self._values.append(v)

        self._update_checks()

    def _update_checks(self):
        if len(self._values) > 0:
            self.set_label('<b>'+self.title+'</b>')
            self.set_use_markup(True)
        else:
            self.set_label(self.title)

        def _set_active(w, active):
            w.disconnect(w._changed_id)
            w.set_active(active)
            w._changed_id = w.connect('toggled', self._on_toggled)

        if not self._multiple_selection:
            if len(self._values) > 0:
                w = self._widgets.get(self._values[0])
                if w:
                    _set_active(w, True)
        else:
            for w in list(self._widgets.values()):
                if w._val in self._values:
                    _set_active(w, True)
                else:
                    _set_active(w, False)

    def _on_toggled(self, w):
        active = w.get_active()
        if not self._multiple_selection and active:
            for v in self._values:
                self._parent_settings.setting_remove_from_list(TypingTweakGroup.XKB_GSETTINGS_NAME, v)

        if w._val in self._values and not active:
            self._parent_settings.setting_remove_from_list(TypingTweakGroup.XKB_GSETTINGS_NAME, w._val)
        elif active and not w._val in self._values and w._val:
            self._parent_settings.setting_add_to_list(TypingTweakGroup.XKB_GSETTINGS_NAME, w._val)

class TypingTweakGroup(Gtk.Box):

    XKB_GSETTINGS_SCHEMA = "org.gnome.desktop.input-sources"
    XKB_GSETTINGS_NAME = "xkb-options"
    # grp_led is unsupported
    XKB_OPTIONS_BLACKLIST = {"grp_led", "Compose key"}

    def __init__(self):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL, spacing=3)
        self._option_objects = []
        ok = False
        try:
            self._kbdsettings = GSettingsSetting(self.XKB_GSETTINGS_SCHEMA)
            self._kdb_settings_id = self._kbdsettings.connect("changed::"+self.XKB_GSETTINGS_NAME, self._on_changed)
            self._xkb_info = GnomeDesktop.XkbInfo()
            ok = True
            self.loaded = True
        except GSettingsMissingError:
            logging.info("Typing missing schema %s" % self.XKB_GSETTINGS_SCHEMA)
            self.loaded = False
        except AttributeError:
            logging.warning("Typing missing GnomeDesktop.gir with Xkb support")
            self.loaded = False
        finally:
            if ok:
                for opt in set(self._xkb_info.get_all_option_groups()) - self.XKB_OPTIONS_BLACKLIST:
                    obj = _XkbOption(opt, self._kbdsettings, self._xkb_info)
                    self._option_objects.append(obj)
                self._option_objects.sort(key=lambda item_desc: item_desc.title)
                for item in self._option_objects: self.pack_start(item, False, False, 0)
        TweakGroup.__init__(self, _("Typing"), *self._option_objects)

        self.connect("destroy", self._on_destroy)

    def _on_changed(self, *args):
        for obj in self._option_objects:
            obj.reload()

    def _on_destroy(self, event):
        if (self._kdb_settings_id):
            self._kbdsettings.disconnect(self._kdb_settings_id)


class KeyThemeSwitcher(GSettingsSwitchTweakValue):
    def __init__(self, **options):
        GSettingsSwitchTweakValue.__init__(self,
                                           _("Emacs Input"),
                                           "org.gnome.desktop.interface",
                                           "gtk-key-theme",
                                           desc=_("Overrides shortcuts to use keybindings from the Emacs editor."),
                                           **options)

    def get_active(self):
        return "Emacs" in self.settings.get_string(self.key_name)

    def set_active(self, v):
        if v:
            self.settings.set_string(self.key_name, "Emacs")
        else:
            self.settings.set_string(self.key_name, "Default")


class OverviewShortcutTweak(Gtk.Box, _GSettingsTweak):

    def __init__(self, **options):
        name = _("Overview Shortcut")
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        _GSettingsTweak.__init__(self, name, "org.gnome.mutter", "overlay-key", loaded=_shell_loaded, **options)

        box_btn = Gtk.ButtonBox()
        box_btn.set_layout(Gtk.ButtonBoxStyle.EXPAND)

        btn1 = Gtk.RadioButton.new_with_label_from_widget(None, _("Left Super"))
        btn1.set_property("draw-indicator", False)

        btn2 = Gtk.RadioButton.new_from_widget(btn1)
        btn2.set_label(_("Right Super"))
        btn2.set_property("draw-indicator", False)

        if (self.settings.get_string(self.key_name) == "Super_R"):
            btn2.set_active(True)
        btn1.connect("toggled", self.on_button_toggled, "Super_L")
        btn2.connect("toggled", self.on_button_toggled, "Super_R")

        box_btn.pack_start(btn1, True, True, 0)
        box_btn.pack_start(btn2, True, True, 0)
        build_label_beside_widget(name, box_btn, hbox=self)

    def on_button_toggled(self, button, key):
        self.settings[self.key_name] = key


class AdditionalLayoutButton(Gtk.Box, Tweak):

    def __init__(self):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL, spacing=18,
                               valign=Gtk.Align.CENTER)
        Tweak.__init__(self, "extensions", "")

        btn = Gtk.Button(label=_("Additional Layout Options"),halign=Gtk.Align.END)
        btn.connect("clicked", self._on_browse_clicked)
        self.add(btn)

        self.show_all()

    def _on_browse_clicked(self, btn):
        dialog = Gtk.Window()
        dialog.set_title(_("Additional Layout Options"))
        dialog.set_type_hint(Gdk.WindowTypeHint.DIALOG)
        dialog.set_transient_for(self.main_window)
        dialog.set_modal(True)

        dialog.set_size_request(500,500)
        geometry = Gdk.Geometry()
        geometry.max_height = 500
        dialog.set_geometry_hints(None, geometry, Gdk.WindowHints.MAX_SIZE)

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_border_width(10)
        box = TypingTweakGroup()
        scrolled_window.add_with_viewport(box)

        dialog.add(scrolled_window)
        dialog.show_all()

class ClickMethod(Gtk.ListBox, Tweak):

    def __init__(self, **options):
        Gtk.ListBox.__init__(self)
        Tweak.__init__(self, _("Mouse Click Emulation"), _("Mouse Click Emulation"))

        self.settings = Gio.Settings("org.gnome.desktop.peripherals.touchpad")
        self.key_name = "click-method"

        self.set_selection_mode(Gtk.SelectionMode.NONE)

        # Needs other page elements to get margins too
        # self.props.margin_left = 50
        # self.props.margin_right = 50

        row = Gtk.ListBoxRow()
        hbox = Gtk.Box()
        hbox.props.margin = 10
        row.add(hbox)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        lbl = Gtk.Label(_("Fingers"), xalign=0)
        lbl.props.xalign = 0.0
        desc = _("Click the touchpad with two fingers for right-click and three fingers for middle-click.")
        lbl_desc = Gtk.Label()
        lbl_desc.set_line_wrap(True)
        lbl_desc.get_style_context().add_class("dim-label")
        lbl_desc.set_markup("<span size='small'>"+GLib.markup_escape_text(desc)+"</span>")

        self.check_fingers = Gtk.Image.new_from_icon_name("object-select-symbolic", Gtk.IconSize.SMALL_TOOLBAR);
        self.check_fingers.set_no_show_all(True)
        self.check_fingers.set_visible(self.settings[self.key_name] == "fingers")

        vbox.pack_start(lbl, False, False, 0)
        vbox.pack_start(lbl_desc, False, False, 0)
        hbox.pack_start(vbox, False, False, 0)
        hbox.pack_end(self.check_fingers, False, False, 0)

        self.add(row)

        row = Gtk.ListBoxRow()
        hbox = Gtk.Box()
        hbox.props.margin = 10
        row.add(hbox)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        lbl = Gtk.Label(_("Area"), xalign=0)
        lbl.props.xalign = 0.0
        desc = _("Click the bottom right of the touchpad for right-click and the bottom middle for middle-click.")
        lbl_desc = Gtk.Label()
        lbl_desc.set_line_wrap(True)
        lbl_desc.get_style_context().add_class("dim-label")
        lbl_desc.set_markup("<span size='small'>"+GLib.markup_escape_text(desc)+"</span>")

        self.check_area = Gtk.Image.new_from_icon_name("object-select-symbolic", Gtk.IconSize.SMALL_TOOLBAR);
        self.check_area.set_no_show_all(True)
        self.check_area.set_visible(self.settings[self.key_name] == "areas")

        vbox.pack_start(lbl, False, False, 0)
        vbox.pack_start(lbl_desc, False, False, 0)
        hbox.pack_start(vbox, False, False, 0)
        hbox.pack_end(self.check_area, False, False, 0)

        self.add(row)

        row = Gtk.ListBoxRow()
        hbox = Gtk.Box()
        hbox.props.margin = 10
        row.add(hbox)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        lbl = Gtk.Label(_("Disabled"), xalign=0)
        lbl.props.xalign = 0.0
        desc = _("Don’t use mouse click emulation.")
        lbl_desc = Gtk.Label()
        lbl_desc.set_line_wrap(True)
        lbl_desc.get_style_context().add_class("dim-label")
        lbl_desc.set_markup("<span size='small'>"+GLib.markup_escape_text(desc)+"</span>")

        self.check_disabled = Gtk.Image.new_from_icon_name("object-select-symbolic", Gtk.IconSize.SMALL_TOOLBAR);
        self.check_disabled.set_no_show_all(True)
        self.check_disabled.set_visible(self.settings[self.key_name] == "none")

        vbox.pack_start(lbl, False, False, 0)
        vbox.pack_start(lbl_desc, False, False, 0)
        hbox.pack_start(vbox, False, False, 0)
        hbox.pack_end(self.check_disabled, False, False, 0)

        self.add(row)
        self.connect('row-activated', self.on_row_clicked)

    def on_row_clicked(self, box, row):
        if row.get_index() == 0:
            self.settings[self.key_name] = "fingers"
            self.check_fingers.show()
            self.check_area.hide()
            self.check_disabled.hide()
        elif row.get_index() == 1:
            self.settings[self.key_name] = "areas"
            self.check_fingers.hide()
            self.check_area.show()
            self.check_disabled.hide()
        else:
            self.settings[self.key_name] = "none"
            self.check_fingers.hide()
            self.check_area.hide()
            self.check_disabled.show()


TWEAK_GROUPS = [ListBoxTweakGroup(_("Keyboard"),
    Title(_("Keyboard"), "", top=True),
    GSettingsSwitchTweak(_("Show Extended Input Sources"),
                          "org.gnome.desktop.input-sources",
                          "show-all-sources",
                          desc=_("Increases the choice of input sources in the Settings application."),
                          logout_required=True,),
    KeyThemeSwitcher(),
    OverviewShortcutTweak(),
    AdditionalLayoutButton(),
)]
