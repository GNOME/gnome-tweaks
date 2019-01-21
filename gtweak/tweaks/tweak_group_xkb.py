# Copyright (c) 2012 Red Hat, Inc.
# Authors:
#       Rui Matos
# SPDX-License-Identifier: GPL-3.0+
# License-Filename: LICENSES/GPL-3.0

import logging

import gi
gi.require_version("GnomeDesktop", "3.0")
from gi.repository import Gtk, GnomeDesktop
from gtweak.tweakmodel import Tweak, TweakGroup
from gtweak.widgets import GSettingsSwitchTweak, build_label_beside_widget, GSettingsComboEnumTweak, GSettingsComboTweak, build_horizontal_sizegroup, ListBoxTweakGroup
from gtweak.gsettings import GSettingsSetting, GSettingsMissingError


class _XkbOption(Gtk.Expander, Tweak):
    def __init__(self, group_id, parent_settings, xkb_info, **options):
        try:
            desc = xkb_info.description_for_group(group_id)
        except AttributeError:
            desc = group_id
        Gtk.Expander.__init__(self)
        Tweak.__init__(self, desc, desc, **options)

        self.set_label(self.name)
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
            self.set_label('<b>'+self.name+'</b>')
            self.set_use_markup(True)
        else:
            self.set_label(self.name)

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
                    self.pack_start(obj, False, False, 0)
        TweakGroup.__init__(self, _("Typing"), *self._option_objects)

        self.connect("destroy", self._on_destroy)

    def _on_changed(self, *args):
        for obj in self._option_objects:
            obj.reload()

    def _on_destroy(self, event):
        if (self._kdb_settings_id):
            self._kbdsettings.disconnect(self._kdb_settings_id)
