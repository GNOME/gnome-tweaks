# Copyright (c) 2011 John Stowers
# SPDX-License-Identifier: GPL-3.0+
# License-Filename: LICENSES/GPL-3.0

import gtweak
from gtweak.tweakmodel import Tweak
from gtweak.widgets import _GSettingsTweak, GSettingsComboEnumTweak, GSettingsSwitchTweakValue, ListBoxTweakGroup, GSettingsComboTweak, GSettingsSwitchTweak, Title, build_label_beside_widget, build_listrow_hbox
from gtweak.utils import XSettingsOverrides
import gettext

from gi.repository import Gio, Gtk, GLib


class Focus(Gtk.ListBox, Tweak):

    def __init__(self, **options):
        Gtk.ListBox.__init__(self)
        Tweak.__init__(self, _("Window Focus"), _("Click to Focus"))
        self.add_css_class("boxed-list")

        self.settings = Gio.Settings("org.gnome.desktop.wm.preferences")
        self.key_name = "focus-mode"

        self.set_selection_mode(Gtk.SelectionMode.NONE)

        row = Gtk.ListBoxRow()
        desc = _("Windows are focused when they are clicked.")
        hbox = build_listrow_hbox(_("Click to Focus"), desc)
        self.check_click = self._create_check_mark("click")
        hbox.append(self.check_click)
        row.set_child(hbox)
        self.append(row)

        row = Gtk.ListBoxRow()
        desc = _("Window is focused when hovered with the pointer. Windows remain focused when the desktop is hovered.")
        hbox = build_listrow_hbox(_("Focus on Hover"), desc)
        self.check_sloppy = self._create_check_mark("sloppy")
        hbox.append(self.check_sloppy)
        row.set_child(hbox)
        self.append(row)

        row = Gtk.ListBoxRow()
        desc = _("Window is focused when hovered with the pointer. Hovering the desktop removes focus from the previous window.")
        hbox = build_listrow_hbox(_("Secondary-Click"), desc)
        self.check_mouse = self._create_check_mark("mouse")
        hbox.append(self.check_mouse)
        row.set_child(hbox)
        self.append(row)

        self.connect('row-activated', self.on_row_clicked)

    def on_row_clicked(self, box, row):
        if row.get_index() == 0:
            self.settings[self.key_name] = "click"
            self.check_click.show()
            self.check_sloppy.hide()
            self.check_mouse.hide()
        elif row.get_index() == 1:
            self.settings[self.key_name] = "sloppy"
            self.check_click.hide()
            self.check_sloppy.show()
            self.check_mouse.hide()
        else:
            self.settings[self.key_name] = "mouse"
            self.check_click.hide()
            self.check_sloppy.hide()
            self.check_mouse.show()

    def _create_check_mark(self, key_name: str) -> Gtk.Image:
        """ Creates an Image check mark with the associated setting

        :param key_name: The setting option to trigger when visible
        :return: Gtk.Image
        """
        check_mark = Gtk.Image.new_from_icon_name("object-select-symbolic")
        check_mark.set_visible(self.settings[self.key_name] == key_name)
        return check_mark


class WindowScalingFactorTweak(Gtk.Box, Tweak):
    def __init__(self, **options):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.HORIZONTAL)
        Tweak.__init__(self, _("Window scaling"), _("Adjust GDK window scaling factor for HiDPI"), **options)

        self._xsettings = XSettingsOverrides()
        self._original_factor = self._xsettings.get_window_scaling_factor()

        w = Gtk.SpinButton.new_with_range(1, 2, 1)
        w.set_numeric(True)
        w.set_digits(0)
        w.set_update_policy(Gtk.SpinButtonUpdatePolicy.IF_VALID)
        w.set_value(self._xsettings.get_window_scaling_factor())
        w.connect("value-changed", self._on_value_changed)

        build_label_beside_widget(self.name, w, hbox=self)
        self.widget_for_size_group = w

    def _timeout_func (self):
        self._countdown -= 1

        if self._countdown == 0:
            self._source = 0
            self._dialog.response(Gtk.ResponseType.NO)
            return False

        self._update_countdown_message()
        self._dialog.format_secondary_text(self._second_message.format(self._countdown))
        return True

    def _update_countdown_message(self):
        self._second_message = gettext.ngettext("Settings will be reverted in {0} second",
                                                "Settings will be reverted in {0} seconds",
                                                self._countdown)

    def _close(self):
        if self._source > 0:
            GLib.Source.remove(self._source)
            self._source = 0

    def _on_value_changed(self, adj):
        if adj.get_value() == self._original_factor:
            return

        self._xsettings.set_window_scaling_factor(adj.get_value())
        self._countdown = 20

        first_message = _("Do you want to keep these HiDPI settings?")
        self._update_countdown_message()

        self._dialog = Gtk.MessageDialog(
                               transient_for=self.main_window,
                               message_type=Gtk.MessageType.QUESTION,
                               text=first_message)
        self._dialog.add_buttons(_("Revert Settings"), Gtk.ResponseType.NO,
                                _("Keep Changes"), Gtk.ResponseType.YES)
        self._dialog.format_secondary_text(self._second_message.format(self._countdown))

        self._source = GLib.timeout_add_seconds(interval=1, function=self._timeout_func)

        response = self._dialog.run()

        if response == Gtk.ResponseType.YES:
            self._original_factor = self._xsettings.get_window_scaling_factor()
        else:
            self._xsettings.set_window_scaling_factor(self._original_factor)
            adj.set_value(self._original_factor)

        self._close()
        self._dialog.destroy()

Title(_("HiDPI"), "", uid="title-hidpi")

depends_how = lambda x,kn: x.get_string(kn) in ("mouse", "sloppy")

class ShowWindowButtons(GSettingsSwitchTweakValue):

    def __init__(self, name, value, **options):
        self.value = value
        GSettingsSwitchTweakValue.__init__(self,
                                           name,
                                           "org.gnome.desktop.wm.preferences",
                                           "button-layout",
                                           **options)
    def get_active(self):
        return self.value in self.settings.get_string(self.key_name)

    def set_active(self, v):
        val = self.settings.get_string(self.key_name)
        (left, colon, right) = val.partition(":")

        if "close" in right:
            rsplit = right.split(",")
            rsplit = [x for x in rsplit if x in ['appmenu', 'minimize', 'maximize', 'close']]

            if v:
                rsplit.append(self.value)
            else:
                rsplit.remove(self.value)

            rsplit.sort(key=lambda x: ["appmenu", "minimize", "maximize", "close"].index(x))

            self.settings.set_string(self.key_name, left + colon + ",".join(rsplit))

        else:
            rsplit = left.split(",")
            rsplit = [x for x in rsplit if x in ['appmenu', 'minimize', 'maximize', 'close']]

            if v:
                rsplit.append(self.value)
            else:
                rsplit.remove(self.value)

            rsplit.sort(key=lambda x: ["close", "minimize", "maximize", "appmenu"].index(x))

            self.settings.set_string(self.key_name, ",".join(rsplit) + colon + right)

class PlaceWindowButtons(Gtk.Box, _GSettingsTweak):

    def __init__(self, **options):
        name = _("Placement")
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.HORIZONTAL, spacing=0)

        _GSettingsTweak.__init__(self,
                                 name,
                                 "org.gnome.desktop.wm.preferences",
                                 "button-layout",
                                 **options)

        box_btn = Gtk.Box()
        box_btn.set_homogeneous(True)
        box_btn.add_css_class("linked")

        # Translators: For RTL languages, this is the "Right" direction since the
        # interface is flipped
        btn1 = Gtk.ToggleButton.new_with_label(_("Left"))
        # Translators: For RTL languages, this is the "Left" direction since the
        # interface is flipped
        btn2 = Gtk.ToggleButton.new_with_label(_("Right"))
        btn2.set_group(btn1)

        val = self.settings.get_string(self.key_name)
        (left, colon, right) = val.partition(":")
        if "close" in right:
           btn2.set_active(True)
        elif "close" in left:
           btn1.set_active(True)
        btn2.connect("toggled", self.on_button_toggled)

        box_btn.append(btn1)
        box_btn.append(btn2)

        build_label_beside_widget(name, box_btn, hbox=self)

    def on_button_toggled(self, v):
        val = self.settings.get_string(self.key_name)
        (left, colon, right) = val.partition(":")

        if "close" in left:
            rsplit = left.split(",")
            rsplit = [x for x in rsplit if x in ['appmenu', 'minimize', 'maximize', 'close']]
            rsplit.sort(key=lambda x: ["appmenu", "minimize", "maximize", "close"].index(x))
            self.settings.set_string(self.key_name, right + colon + ",".join(rsplit))
        else:
            rsplit = right.split(",")
            rsplit = [x for x in rsplit if x in ['appmenu', 'minimize', 'maximize', 'close']]
            rsplit.sort(key=lambda x: ["close", "minimize", "maximize", "appmenu"].index(x))
            self.settings.set_string(self.key_name, ",".join(rsplit) + colon + left)


TWEAK_GROUP = ListBoxTweakGroup("window-management", _("Windows"),
    Title(_("Titlebar Actions"), "", uid="title-titlebar-actions"),
    GSettingsComboEnumTweak(_("Double-Click"),"org.gnome.desktop.wm.preferences", "action-double-click-titlebar"),
    GSettingsComboEnumTweak(_("Middle-Click"),"org.gnome.desktop.wm.preferences", "action-middle-click-titlebar"),
    GSettingsComboEnumTweak(_("Secondary-Click"),"org.gnome.desktop.wm.preferences", "action-right-click-titlebar"),
    Title(_("Titlebar Buttons"), "", uid="title-theme"),
    ShowWindowButtons(_("Maximize"), "maximize"),
    ShowWindowButtons(_("Minimize"), "minimize"),
    PlaceWindowButtons(),
      Title(_("Click Actions"), "", uid="title-window-behavior"),
    GSettingsSwitchTweak(_("Attach Modal Dialogs"),"org.gnome.mutter", "attach-modal-dialogs",
                    desc=_("When on, modal dialog windows are attached to their parent windows, and cannot be moved.")),
    GSettingsSwitchTweak(_("Center New Windows"),"org.gnome.mutter", "center-new-windows"),
    GSettingsComboTweak(_("Window Action Key"),
                    "org.gnome.desktop.wm.preferences",
                    "mouse-button-modifier",
                    [("disabled", _("Disabled")), ("<Alt>", "Alt"), ("<Super>", "Super")]),
    GSettingsSwitchTweak(_("Resize with Secondary-Click"),"org.gnome.desktop.wm.preferences", "resize-with-right-button"),
    Title(_("Focusing"), _("Click to Focus"), uid="title-theme"),
    Focus(),
    GSettingsSwitchTweak(_("Raise Windows When Focused"),"org.gnome.desktop.wm.preferences", "auto-raise", depends_on=Focus(), depends_how=depends_how),
)


