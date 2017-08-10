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

import gtweak
from gtweak.gshellwrapper import GnomeShellFactory
from gtweak.tweakmodel import Tweak
from gtweak.widgets import ListBoxTweakGroup, GSettingsComboEnumTweak, GSettingsComboTweak, GSettingsSwitchTweak, Title, GSettingsSwitchTweakValue, build_label_beside_widget, _GSettingsTweak
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

        lbl = Gtk.Label(_("Sloppy"), xalign=0)
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

        box_btn = Gtk.ButtonBox()
        box_btn.set_layout(Gtk.ButtonBoxStyle.EXPAND)

        # Translators: For RTL languages, this is the "Right" direction since the
        # interface is flipped
        btn1 = Gtk.RadioButton.new_with_label_from_widget(None, _("Left"))
        btn1.set_property("draw-indicator", False)

        btn2 = Gtk.RadioButton.new_from_widget(btn1)
        # Translators: For RTL languages, this is the "Left" direction since the
        # interface is flipped
        btn2.set_label(_("Right"))
        btn2.set_property("draw-indicator", False)

        val = self.settings.get_string(self.key_name)
        (left, colon, right) = val.partition(":")
        if "close" in right:
           btn2.set_active(True)
        btn2.connect("toggled", self.on_button_toggled)

        box_btn.pack_start(btn1, True, True, 0)
        box_btn.pack_start(btn2, True, True, 0)

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
        self._dialog.format_secondary_text(self._second_message % self._countdown)
        return True

    def _update_countdown_message(self):
        self._second_message = gettext.ngettext("Settings will be reverted in %d second",
                                                "Settings will be reverted in %d seconds",
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
        self._dialog.format_secondary_text(self._second_message % self._countdown)

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
        GSettingsSwitchTweak(_("Resize with Secondary-Click"),"org.gnome.desktop.wm.preferences", "resize-with-right-button"),
        GSettingsComboTweak(_("Window Action Key"),
                        "org.gnome.desktop.wm.preferences",
                        "mouse-button-modifier",
                        [("disabled", _("Disabled")), ("<Alt>", "Alt"), ("<Super>", "Super")]),
        Title(_("Window Focus"), _("Click to Focus"), uid="title-theme"),
        Focus(),
        GSettingsSwitchTweak(_("Raise Windows When Focused"),"org.gnome.desktop.wm.preferences", "auto-raise", depends_on=Focus(), depends_how=depends_how),
        Title(_("Titlebar Actions"), "", uid="title-titlebar-actions"),
        GSettingsComboEnumTweak(_("Double-Click"),"org.gnome.desktop.wm.preferences", "action-double-click-titlebar"),
        GSettingsComboEnumTweak(_("Middle-Click"),"org.gnome.desktop.wm.preferences", "action-middle-click-titlebar"),
        GSettingsComboEnumTweak(_("Secondary-Click"),"org.gnome.desktop.wm.preferences", "action-right-click-titlebar"),
        Title(_("Titlebar Buttons"), "", uid="title-theme"),
        ShowWindowButtons(_("Maximize"), "maximize"),
        ShowWindowButtons(_("Minimize"), "minimize"),
        PlaceWindowButtons(),
    )
]

