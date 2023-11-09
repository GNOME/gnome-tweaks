# Copyright (c) 2011 John Stowers
# SPDX-License-Identifier: GPL-3.0+
# License-Filename: LICENSES/GPL-3.0

from gtweak.tweakmodel import Tweak
from gtweak.widgets import UI_BOX_HORIZONTAL_SPACING, UI_BOX_SPACING, _GSettingsTweak, GSettingsComboEnumTweak, GSettingsSwitchTweakValue, ListBoxTweakGroup, GSettingsComboTweak, GSettingsSwitchTweak, ListBoxTweakSubgroup, build_label_beside_widget, TickActionRow
from gtweak.utils import XSettingsOverrides
import gettext

from gi.repository import Gio, Gtk, GLib


# TODO: Unify code for "check" group row
class Focus(ListBoxTweakSubgroup, Tweak):

    def __init__(self, *tweaks, **options):
        name: str = _("Window Focus")
        desc: str = _("Click to Focus")
        ListBoxTweakSubgroup.__init__(self, title=name, name="focus")
        Tweak.__init__(self, name, desc, **options)


        self.settings = Gio.Settings("org.gnome.desktop.wm.preferences")
        self.key_name = "focus-mode"

        self.row_click = self._setup_action_row(
            key_name="click", title=_("Click to Focus"),
            subtitle=_(
                "Windows are focused when they are clicked."))

        self.row_sloppy = self._setup_action_row(
            key_name="sloppy", title=_("Focus on Hover"),
            subtitle=_(
                "Window is focused when hovered with the pointer. Windows remain focused when the desktop is hovered."))

        self.row_mouse = self._setup_action_row(
            key_name="mouse", title=_("Secondary-Click"),
            subtitle=_(
                "Window is focused when hovered with the pointer. Hovering the desktop removes focus "
                "from the previous window."))
            
        self.settings.connect("changed", self._settings_changed)

        for t in tweaks:
            self.add_tweak_row(t)

        

    def _setup_action_row(self, key_name: str, title: str, subtitle: str):
        action_row = TickActionRow(title, subtitle, key_name)
        action_row.img.set_visible(self.settings[self.key_name] == key_name)
        action_row.connect("activated", self._on_row_clicked)

        self.add(action_row)
        return action_row

    def _settings_changed(self, settings, key: str):
        keyvalue = settings[key]
        if keyvalue == "click":
            self.row_click.img.show()
            self.row_sloppy.img.hide()
            self.row_mouse.img.hide()
        elif keyvalue == "sloppy":
            self.row_click.img.hide()
            self.row_sloppy.img.show()
            self.row_mouse.img.hide()
        else:  # mouse
            self.row_click.img.hide()
            self.row_sloppy.img.hide()
            self.row_mouse.img.show()

    def _on_row_clicked(self, row: TickActionRow):
        self.settings[self.key_name] = row.keyvalue

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
        Tweak.__init__(self, _("Window scaling"), _("Adjust GDK window scaling factor for HiDPI"),
                       **options)

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

    def _timeout_func(self):
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
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.HORIZONTAL, margin_start=UI_BOX_HORIZONTAL_SPACING, margin_end=UI_BOX_HORIZONTAL_SPACING,
                         margin_top=UI_BOX_SPACING, margin_bottom=UI_BOX_SPACING,spacing=0)

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


TWEAK_GROUP = ListBoxTweakGroup(
    "window-management", _("Windows"),
    ListBoxTweakSubgroup(
        _("Titlebar Actions"), "title-titlebar-actions",
        GSettingsComboEnumTweak(_("Double-Click"),"org.gnome.desktop.wm.preferences", "action-double-click-titlebar"),
        GSettingsComboEnumTweak(_("Middle-Click"),"org.gnome.desktop.wm.preferences", "action-middle-click-titlebar"),
        GSettingsComboEnumTweak(_("Secondary-Click"),"org.gnome.desktop.wm.preferences", "action-right-click-titlebar"),
    ), 
    ListBoxTweakSubgroup(_("Titlebar Buttons"), "title-theme",
        ShowWindowButtons(_("Maximize"), "maximize"),
        ShowWindowButtons(_("Minimize"), "minimize"),
        PlaceWindowButtons()
    ),
    ListBoxTweakSubgroup(
        _("Click Actions"), "title-window-behavior",
        GSettingsSwitchTweak(_("Attach Modal Dialogs"),"org.gnome.mutter", "attach-modal-dialogs",
                        desc=_("When on, modal dialog windows are attached to their parent windows, and cannot be moved.")),
        GSettingsSwitchTweak(_("Center New Windows"),"org.gnome.mutter", "center-new-windows"),
        GSettingsComboTweak(_("Window Action Key"),
                        "org.gnome.desktop.wm.preferences",
                        "mouse-button-modifier",
                        [("disabled", _("Disabled")), ("<Alt>", "Alt"), ("<Super>", "Super")]),
  
    
        GSettingsSwitchTweak(_("Resize with Secondary-Click"),"org.gnome.desktop.wm.preferences", "resize-with-right-button"),
     ),
 
    Focus(GSettingsSwitchTweak(_("Raise Windows When Focused"),"org.gnome.desktop.wm.preferences", "auto-raise", depends_on=Focus(), depends_how=depends_how)),
      
)    

