# Copyright (c) 2011 John Stowers
# SPDX-License-Identifier: GPL-3.0+
# License-Filename: LICENSES/GPL-3.0

import logging

from gi.repository import Gio, Gtk

from gtweak.tweakmodel import Tweak
from gtweak.widgets import ListBoxTweakGroup, GSettingsSpinButtonTweak, GSettingsFontButtonTweak
from gtweak.gsettings import GSettingsSetting

class FontXSettingsTweak(Gtk.FlowBox, Tweak):

    def __init__(self, **options):
        Gtk.FlowBox.__init__(self,
                             orientation=Gtk.Orientation.HORIZONTAL,
                             column_spacing=12,
                             row_spacing=12,
                             homogeneous=True,
                             hexpand=True,
                             selection_mode=Gtk.SelectionMode.NONE,
        )
        Tweak.__init__(self, _("Hinting"), _("Antialiasing"))
        
        try:
            self.settings = GSettingsSetting("org.gnome.desktop.interface")
        except:
            self.settings = None
            logging.warn("org.gnome.desktop.interface not installed or running")
        
        if not self.settings:
            return

        self.props.margin_top = 12

        label = Gtk.Label(_("Hinting"))
        label.props.yalign = 0.0
        label.padding = 10

        hint_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        hint_box.props.hexpand = True

        hint_options_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
       
        hint_box.add(label)
        hint_box.add(hint_options_box)

        self.add(hint_box)

        self.btn_full = Gtk.RadioButton.new_from_widget(None)
        self.btn_full.set_label(_("Full"))
        self.btn_full.set_active(self.settings["font-hinting"] == "full")
        self.btn_full.connect("toggled", self.on_hint_button_toggled)
        hint_options_box.pack_start(self.btn_full, False, False, 0)

        self.btn_med = Gtk.RadioButton.new_from_widget(self.btn_full)
        self.btn_med.set_label(_("Medium"))
        self.btn_med.set_active(self.settings["font-hinting"] == "medium")
        self.btn_med.connect("toggled", self.on_hint_button_toggled)
        hint_options_box.pack_start(self.btn_med, False, False, 0)

        self.btn_slight = Gtk.RadioButton.new_from_widget(self.btn_full)
        self.btn_slight.set_label(_("Slight"))
        self.btn_slight.set_active(self.settings["font-hinting"] == "slight")
        self.btn_slight.connect("toggled", self.on_hint_button_toggled)
        hint_options_box.pack_start(self.btn_slight, False, False, 0)

        self.btn_hnone = Gtk.RadioButton.new_from_widget(self.btn_full)
        self.btn_hnone.set_label(_("None"))
        self.btn_hnone.set_active(self.settings["font-hinting"] == "none")
        self.btn_hnone.connect("toggled", self.on_hint_button_toggled)
        hint_options_box.pack_start(self.btn_hnone, False, False, 0)

        label = Gtk.Label(_("Antialiasing"))
        label.props.yalign = 0.0

        aa_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        aa_box.props.hexpand = True

        aa_options_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        aa_box.add(label)
        aa_box.add(aa_options_box)

        self.add(aa_box)

        self.btn_rgba = Gtk.RadioButton.new_from_widget(None)
        self.btn_rgba.set_label(_("Subpixel (for LCD screens)"))
        self.btn_rgba.set_active(self.settings["font-antialiasing"] == "rgba")
        self.btn_rgba.connect("toggled", self.on_aa_button_toggled)
        aa_options_box.pack_start(self.btn_rgba, False, False, 0)

        self.btn_gray = Gtk.RadioButton.new_from_widget(self.btn_rgba)
        self.btn_gray.set_label(_("Standard (grayscale)"))
        self.btn_gray.set_active(self.settings["font-antialiasing"] == "grayscale")
        self.btn_gray.connect("toggled", self.on_aa_button_toggled)
        aa_options_box.pack_start(self.btn_gray, False, False, 0)

        self.btn_anone = Gtk.RadioButton.new_from_widget(self.btn_rgba)
        self.btn_anone.set_label(_("None"))
        self.btn_anone.set_active(self.settings["font-antialiasing"] == "none")
        self.btn_anone.connect("toggled", self.on_aa_button_toggled)
        aa_options_box.pack_start(self.btn_anone, False, False, 0)

    def on_hint_button_toggled(self, button):
        if self.btn_full.get_active():
            self.settings["font-hinting"] ="full"
        elif self.btn_med.get_active():
            self.settings["font-hinting"] = "medium"
        elif self.btn_slight.get_active():
            self.settings["font-hinting"] = "slight"
        else:
            print("none")
            self.settings["font-hinting"] = "none"

    def on_aa_button_toggled(self, button):
        if self.btn_rgba.get_active():
            self.settings["font-antialiasing"] = "rgba"
        elif self.btn_gray.get_active():
            self.settings["font-antialiasing"] = "grayscale"
        else:
            self.settings["font-antialiasing"] = "none"

TWEAK_GROUP = ListBoxTweakGroup("fonts", _("Fonts"),
    GSettingsFontButtonTweak(_("Interface Text"),"org.gnome.desktop.interface", "font-name"),
    GSettingsFontButtonTweak(_("Document Text"), "org.gnome.desktop.interface", "document-font-name"),
    GSettingsFontButtonTweak(_("Monospace Text"), "org.gnome.desktop.interface", "monospace-font-name"),
    GSettingsFontButtonTweak(_("Legacy Window Titles"),"org.gnome.desktop.wm.preferences", "titlebar-font"),
    FontXSettingsTweak(),
    GSettingsSpinButtonTweak(_("Scaling Factor"),
      "org.gnome.desktop.interface", "text-scaling-factor",
      adjustment_step=0.01, digits=2),
)

