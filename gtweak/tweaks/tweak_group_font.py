# Copyright (c) 2011 John Stowers
# SPDX-License-Identifier: GPL-3.0+
# License-Filename: LICENSES/GPL-3.0

import logging
from typing import Callable, Optional

from gi.repository import Gtk

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

        label = Gtk.Label(label=_("Hinting"))
        label.props.yalign = 0.0
        label.padding = 10

        hint_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        hint_box.props.hexpand = True

        hint_options_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
       
        hint_box.append(label)
        hint_box.append(hint_options_box)

        self.prepend(hint_box)

        self.btn_full = Gtk.CheckButton.new_with_label(_("Full"))
        self.btn_full.set_active(self.settings["font-hinting"] == "full")
        self.btn_full.connect("toggled", self.on_hint_button_toggled)
        hint_options_box.prepend(self.btn_full)

        self.btn_med = Gtk.CheckButton.new_with_label(_("Medium"))
        self.btn_med.set_group(self.btn_full)
        self.btn_med.set_active(self.settings["font-hinting"] == "medium")
        self.btn_med.connect("toggled", self.on_hint_button_toggled)
        hint_options_box.prepend(self.btn_med)

        self.btn_slight = Gtk.CheckButton.new_with_label(_("Slight"))
        self.btn_slight.set_group(self.btn_full)
        self.btn_slight.set_active(self.settings["font-hinting"] == "slight")
        self.btn_slight.connect("toggled", self.on_hint_button_toggled)
        hint_options_box.prepend(self.btn_slight)

        self.btn_hnone = Gtk.CheckButton.new_with_label(_("None"))
        self.btn_hnone.set_group(self.btn_full)
        self.btn_hnone.set_active(self.settings["font-hinting"] == "none")
        self.btn_hnone.connect("toggled", self.on_hint_button_toggled)
        hint_options_box.prepend(self.btn_hnone)

        label = Gtk.Label(label=_("Antialiasing"))
        label.props.yalign = 0.0

        aa_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        aa_box.props.hexpand = True

        aa_options_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        aa_box.append(label)
        aa_box.append(aa_options_box)

        self.prepend(aa_box)

        self.btn_rgba = Gtk.CheckButton.new_with_label(_("Subpixel (for LCD screens)"))
        self.btn_rgba.set_active(self.settings["font-antialiasing"] == "rgba")
        self.btn_rgba.connect("toggled", self.on_aa_button_toggled)
        aa_options_box.prepend(self.btn_rgba)

        self.btn_gray = Gtk.CheckButton.new_with_label(_("Standard (grayscale)"))
        self.btn_gray.set_group(self.btn_rgba)
        self.btn_gray.set_active(self.settings["font-antialiasing"] == "grayscale")
        self.btn_gray.connect("toggled", self.on_aa_button_toggled)
        aa_options_box.prepend(self.btn_gray)

        self.btn_anone = Gtk.CheckButton.new_with_label(_("None"))
        self.btn_anone.set_group(self.btn_rgba)
        self.btn_anone.set_active(self.settings["font-antialiasing"] == "none")
        self.btn_anone.connect("toggled", self.on_aa_button_toggled)
        aa_options_box.prepend(self.btn_anone)

    @staticmethod
    def _create_check_btn(
        label: str,
        is_active: bool,
        connect_function: Callable,
        btn_group: Optional[Gtk.CheckButton] = None
    ) -> Gtk.CheckButton:

        btn_check = Gtk.CheckButton.new_with_label(label)
        btn_check.set_active(is_active)
        if btn_group is not None:
            btn_check.set_group(btn_group)
        btn_check.connect("toggled", connect_function)

        return btn_check

    def on_hint_button_toggled(self, button: Gtk.CheckButton):
        if button is self.btn_full:
            self.settings["font-hinting"] = "full"
        elif button is self.btn_med:
            self.settings["font-hinting"] = "medium"
        elif button is self.btn_slight:
            self.settings["font-hinting"] = "slight"
        else:
            self.settings["font-hinting"] = "none"

    def on_aa_button_toggled(self, button: Gtk.CheckButton):
        if button is self.btn_rgba:
            self.settings["font-antialiasing"] = "rgba"
        elif button is self.btn_gray:
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

