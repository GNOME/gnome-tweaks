# Copyright (c) 2011 John Stowers
# SPDX-License-Identifier: GPL-3.0+
# License-Filename: LICENSES/GPL-3.0

import os.path

from gi.repository import Gio, GLib, Gtk, Gdk

import gtweak
from gtweak.gshellwrapper import GnomeShellFactory
from gtweak.tweaks.tweak_group_xkb import TypingTweakGroup
from gtweak.widgets import ListBoxTweakGroup, GSettingsSwitchTweak, GSettingsSwitchTweakValue, _GSettingsTweak, Title, GSettingsComboEnumTweak, build_label_beside_widget, Tweak, UI_BOX_SPACING

_shell = GnomeShellFactory().get_shell()
_shell_loaded = _shell is not None


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


class ComposeDialogLauncher(Gtk.Box, _GSettingsTweak):

    def __init__(self, **options):
        name = _("Compose Key")
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.HORIZONTAL, spacing=18)
        _GSettingsTweak.__init__(self, name, "org.gnome.desktop.input-sources", "xkb-options", **options)

        key_values = ["compose:sclk", "compose:prsc", "compose:menu", "compose:ralt", "compose:rctrl", "compose:rwin", "compose:caps", "compose:lctrl"]
        key_names = [_("Scroll Lock"), _("PrtScn"), _("Menu"), _("Right Alt"), _("Right Ctrl"), _("Right Super"), _("Caps Lock"), _("Left Ctrl")]

        button = Gtk.Button(_("Disabled"), halign=Gtk.Align.END)
        button.set_relief(Gtk.ReliefStyle.NONE)
        button.connect("clicked", self.on_button_clicked, self.settings)

        desc = _("Allows entering additional characters.")

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        vbox.props.spacing = UI_BOX_SPACING

        lbl = Gtk.Label(name)
        lbl.props.xalign = 0.0
        lbl_desc = Gtk.Label()
        lbl_desc.set_line_wrap(True)
        lbl_desc.get_style_context().add_class("dim-label")
        lbl_desc.set_markup("<span size='small'>"+GLib.markup_escape_text(desc)+"</span>")

        vbox.pack_start(lbl, False, False, 0)
        vbox.pack_start(lbl_desc, False, False, 0)
        self.pack_start(vbox, False, False, 0)
        self.pack_end(button, True, True, 0)

        for index, item in enumerate(key_values):
            if self.settings.setting_is_in_list("xkb-options", item):
                button.set_label(key_names[index])
                # We only support one Compose key so drop any one other set keys
                for extra in key_values:
                    self.settings.setting_remove_from_list("xkb-options", extra)
                self.settings.setting_add_to_list("xkb-options", item)

    def on_button_clicked(self, widget, settings):
        a = ComposeDialog(self.main_window, widget, settings)
        resp = a.run()
        a.destroy()


class ComposeDialog(Gtk.Dialog, Gtk.Button):
    key_values = ["compose:sclk", "compose:prsc", "compose:menu", "compose:ralt", "compose:rctrl", "compose:rwin", "compose:caps", "compose:lctrl"]
    key_names = [_("Scroll Lock"), _("PrtScn"), _("Menu"), _("Right Alt"), _("Right Ctrl"), _("Right Super"), _("Caps Lock"), _("Left Ctrl")]

    def __init__(self, parent, parent_button, settings):
        Gtk.Dialog.__init__(self)

        geometry = Gdk.Geometry()
        geometry.max_width = 500
        self.set_geometry_hints(None, geometry, Gdk.WindowHints.MAX_SIZE)
        self.set_modal(True)
        self.set_transient_for(parent)
        self.set_size_request(500,-1)

        btn_sclk = Gtk.RadioButton.new_with_label_from_widget(None, _("Scroll Lock"))
        btn_prsc = Gtk.RadioButton.new_with_label_from_widget(btn_sclk, _("PrtScn"))
        btn_menu = Gtk.RadioButton.new_with_label_from_widget(btn_sclk, _("Menu"))
        btn_ralt = Gtk.RadioButton.new_with_label_from_widget(btn_sclk, _("Right Alt"))
        btn_rctrl = Gtk.RadioButton.new_with_label_from_widget(btn_sclk, _("Right Ctrl"))
        btn_rwin = Gtk.RadioButton.new_with_label_from_widget(btn_sclk, _("Right Super"))
        btn_caps = Gtk.RadioButton.new_with_label_from_widget(btn_sclk, _("Caps Lock"))
        btn_lctrl = Gtk.RadioButton.new_with_label_from_widget(btn_sclk, _("Left Ctrl"))
        compose_buttons= [btn_sclk, btn_prsc, btn_menu, btn_ralt, btn_rctrl, btn_rwin, btn_caps, btn_lctrl]

        hb = Gtk.HeaderBar()
        hb.set_show_close_button(True)
        hb.props.title = _("Compose Key")
        self.set_titlebar(hb)

        switch = Gtk.Switch()
        compose_enabled = False
        for item in self.key_values:
            if settings.setting_is_in_list("xkb-options", item):
                 compose_enabled = True
        switch.set_active(compose_enabled)
        for button in compose_buttons:
           button.set_sensitive(compose_enabled)
        switch.connect("notify::active", self._on_switch_changed, parent_button, compose_buttons, settings)

        hb.pack_start(switch)

        grid = Gtk.Grid()
        grid.props.border_width = 18
        label = Gtk.Label(None)
        label.set_markup(_("The compose key allows a wide variety of characters to be entered. To use it, press the compose key and then a sequence of characters.\n\n"
            "Many unusual characters can be entered by combining standard ones. For example, compose key followed by <b>C</b> and <b>o</b> will enter <b>©</b>, <b>a</b> followed by <b>'</b> will enter <b>á</b>.\n"))
        label.set_line_wrap(True)
        self.get_content_area().pack_start(grid, True, True, 0)

        grid.attach(label, 0, 0, 4, 1)
        grid.attach(btn_sclk, 1, 1, 1, 1)
        grid.attach(btn_prsc, 1, 2, 1, 1)
        grid.attach(btn_menu, 1, 3, 1, 1)
        grid.attach(btn_ralt, 2, 1, 1, 1)
        grid.attach(btn_rctrl, 2, 2, 1, 1)
        grid.attach(btn_rwin, 2, 3, 1, 1)
        grid.attach(btn_caps, 3, 1, 1, 1)
        grid.attach(btn_lctrl, 3, 2, 1, 1)

        if settings.setting_is_in_list("xkb-options", "compose:sclk"):
            btn_sclk.set_active(True)
        elif settings.setting_is_in_list("xkb-options", "compose:prsc"):
            btn_prsc.set_active(True)
        elif settings.setting_is_in_list("xkb-options", "compose:menu"):
            btn_menu.set_active(True)
        elif settings.setting_is_in_list("xkb-options", "compose:ralt"):
            btn_ralt.set_active(True)
        elif settings.setting_is_in_list("xkb-options", "compose:rctrl"):
            btn_rctrl.set_active(True)
        elif settings.setting_is_in_list("xkb-options", "compose:rwin"):
            btn_rwin.set_active(True)
        elif settings.setting_is_in_list("xkb-options", "compose:caps"):
            btn_caps.set_active(True)
        elif settings.setting_is_in_list("xkb-options", "compose:lctrl"):
            btn_lctrl.set_active(True)

        for index, button in enumerate(compose_buttons):
           button.set_sensitive(compose_enabled)
           button.connect("toggled", self.on_button_toggled, index, parent_button, settings)

        self.show_all()

    def on_button_toggled(self, button, index, parent_button, settings):
        for item in self.key_values:
            settings.setting_remove_from_list("xkb-options", item)
        settings.setting_add_to_list("xkb-options", self.key_values[index])
        parent_button.set_label(self.key_names[index])

    def _on_switch_changed(self, switch, param, parent_button, compose_buttons, settings):
        compose_enabled = switch.get_active()
        for button in compose_buttons:
           button.set_sensitive(compose_enabled)
        # Until we implement storing the old Compose key setting somewhere,
        # just force the key to Scroll Lock since it's first in the list.
        if compose_enabled:
            settings.setting_add_to_list("xkb-options", "compose:sclk")
            parent_button.set_label(_("Scroll Lock"))
        else:
            compose_buttons[0].set_active(True)
            for item in self.key_values:
                settings.setting_remove_from_list("xkb-options", item)
            parent_button.set_label(_("Disabled"))


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


TWEAK_GROUPS = [
    ListBoxTweakGroup(_("Keyboard & Mouse"),
        Title(_("Keyboard"), "", top=True),
        GSettingsSwitchTweak(_("Show Extended Input Sources"),
                              "org.gnome.desktop.input-sources",
                              "show-all-sources",
                              desc=_("Increases the choice of input sources in the Settings application."),
                              logout_required=True,),
        KeyThemeSwitcher(),
        ComposeDialogLauncher(),
        OverviewShortcutTweak(),
        AdditionalLayoutButton(),
        Title(_("Mouse"), ""),
        GSettingsComboEnumTweak(_("Acceleration Profile"),
                                "org.gnome.desktop.peripherals.mouse",
                                "accel-profile",
                                schema_filename="org.gnome.desktop.peripherals.gschema.xml"),
        GSettingsSwitchTweak(_("Pointer Location"),
                             "org.gnome.desktop.interface",
                             "locate-pointer",
                              desc=_("Press the Ctrl key to highlight the pointer.")),
        GSettingsSwitchTweak(_("Middle Click Paste"),
                             "org.gnome.desktop.interface",
                             "gtk-enable-primary-paste"),

        Title(_("Touchpad"), ""),
        GSettingsSwitchTweak(_("Disable While Typing"),
                             "org.gnome.desktop.peripherals.touchpad",
                             "disable-while-typing",
                             schema_filename="org.gnome.desktop.peripherals.gschema.xml"),
        Title(_("Mouse Click Emulation"), _("Mouse Click Emulation"), top=True),
        ClickMethod(),
        ),
]
