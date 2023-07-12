# Copyright (c) 2011 John Stowers
# SPDX-License-Identifier: GPL-3.0+
# License-Filename: LICENSES/GPL-3.0


from gi.repository import Gio, GLib, Gtk

from gtweak.gshellwrapper import GnomeShellFactory
from gtweak.widgets import ListBoxTweakGroup, GSettingsSwitchTweak, GSettingsSwitchTweakValue, _GSettingsTweak, Title, GSettingsComboEnumTweak, build_label_beside_widget, Tweak

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


TWEAK_GROUP = ListBoxTweakGroup("mouse", _("Mouse"),
    Title(_("Mouse"), ""),
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
)
