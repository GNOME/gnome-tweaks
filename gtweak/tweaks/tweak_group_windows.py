# Copyright (c) 2011 John Stowers
# SPDX-License-Identifier: GPL-3.0+
# License-Filename: LICENSES/GPL-3.0

import gtweak
from gtweak.tweakmodel import Tweak
from gtweak.widgets import ListBoxTweakGroup, GSettingsComboTweak, GSettingsSwitchTweak, Title, build_label_beside_widget
from gtweak.utils import XSettingsOverrides
import gettext

from gi.repository import Gio, Gtk, GLib


class Focus(Gtk.ListBox, Tweak):

    def __init__(self, **options):
        Gtk.ListBox.__init__(self)
        Tweak.__init__(self, _("Window Focus"), _("Click to Focus"))

        self.settings = Gio.Settings("org.gnome.desktop.wm.preferences")
        self.key_name = "focus-mode"

        self.set_selection_mode(Gtk.SelectionMode.NONE)

        # Needs other page elements to get margins too
        # self.props.margin_left = 50
        # self.props.margin_right = 50

        row = Gtk.ListBoxRow()
        hbox = Gtk.Box()
        hbox.props.margin = 10
        row.add(hbox)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        lbl = Gtk.Label(_("Click to Focus"), xalign=0)
        lbl.props.xalign = 0.0
        desc = _("Windows are focused when they are clicked.")
        lbl_desc = Gtk.Label()
        lbl_desc.set_line_wrap(True)
        lbl_desc.get_style_context().add_class("dim-label")
        lbl_desc.set_markup("<span size='small'>"+GLib.markup_escape_text(desc)+"</span>")

        self.check_click = Gtk.Image.new_from_icon_name("object-select-symbolic", Gtk.IconSize.SMALL_TOOLBAR);
        self.check_click.set_no_show_all(True)
        self.check_click.set_visible(self.settings[self.key_name] == "click")

        vbox.pack_start(lbl, False, False, 0)
        vbox.pack_start(lbl_desc, False, False, 0)
        hbox.pack_start(vbox, False, False, 0)
        hbox.pack_end(self.check_click, False, False, 0)

        self.add(row)

        row = Gtk.ListBoxRow()
        hbox = Gtk.Box()
        hbox.props.margin = 10
        row.add(hbox)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        lbl = Gtk.Label(_("Focus on Hover"), xalign=0)
        lbl.props.xalign = 0.0
        desc = _("Window is focused when hovered with the pointer. Windows remain focused when the desktop is hovered.")
        lbl_desc = Gtk.Label()
        lbl_desc.set_line_wrap(True)
        lbl_desc.get_style_context().add_class("dim-label")
        lbl_desc.set_markup("<span size='small'>"+GLib.markup_escape_text(desc)+"</span>")

        self.check_sloppy = Gtk.Image.new_from_icon_name("object-select-symbolic", Gtk.IconSize.SMALL_TOOLBAR);
        self.check_sloppy.set_no_show_all(True)
        self.check_sloppy.set_visible(self.settings[self.key_name] == "sloppy")

        vbox.pack_start(lbl, False, False, 0)
        vbox.pack_start(lbl_desc, False, False, 0)
        hbox.pack_start(vbox, False, False, 0)
        hbox.pack_end(self.check_sloppy, False, False, 0)

        self.add(row)

        row = Gtk.ListBoxRow()
        hbox = Gtk.Box()
        hbox.props.margin = 10
        row.add(hbox)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        lbl = Gtk.Label(_("Secondary-Click"), xalign=0)
        lbl.props.xalign = 0.0
        desc = _("Window is focused when hovered with the pointer. Hovering the desktop removes focus from the previous window.")
        lbl_desc = Gtk.Label()
        lbl_desc.set_line_wrap(True)
        lbl_desc.get_style_context().add_class("dim-label")
        lbl_desc.set_markup("<span size='small'>"+GLib.markup_escape_text(desc)+"</span>")

        self.check_mouse = Gtk.Image.new_from_icon_name("object-select-symbolic", Gtk.IconSize.SMALL_TOOLBAR);
        self.check_mouse.set_no_show_all(True)
        self.check_mouse.set_visible(self.settings[self.key_name] == "mouse")

        vbox.pack_start(lbl, False, False, 0)
        vbox.pack_start(lbl_desc, False, False, 0)
        hbox.pack_start(vbox, False, False, 0)
        hbox.pack_end(self.check_mouse, False, False, 0)

        self.add(row)
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


TWEAK_GROUPS = [
    ListBoxTweakGroup(_("Windows"),
        GSettingsSwitchTweak(_("Attach Modal Dialogs"),"org.gnome.mutter", "attach-modal-dialogs",
                        desc=_("When on, modal dialog windows are attached to their parent windows, and cannot be moved.")),
        # https://help.gnome.org/users/gnome-help/stable/shell-windows-tiled.html
        GSettingsSwitchTweak(_("Edge Tiling"),"org.gnome.mutter", "edge-tiling",
                        desc=_("When on, windows are tiled when dragged to screen edges.")),
        GSettingsSwitchTweak(_("Center New Windows"),"org.gnome.mutter", "center-new-windows"),
        GSettingsSwitchTweak(_("Resize with Secondary-Click"),"org.gnome.desktop.wm.preferences", "resize-with-right-button"),
        GSettingsComboTweak(_("Window Action Key"),
                        "org.gnome.desktop.wm.preferences",
                        "mouse-button-modifier",
                        [("disabled", _("Disabled")), ("<Alt>", "Alt"), ("<Super>", "Super")]),
        Title(_("Window Focus"), _("Click to Focus"), uid="title-theme"),
        Focus(),
        GSettingsSwitchTweak(_("Raise Windows When Focused"),"org.gnome.desktop.wm.preferences", "auto-raise", depends_on=Focus(), depends_how=depends_how),
    )
]

