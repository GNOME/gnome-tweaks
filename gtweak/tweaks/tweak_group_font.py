# Copyright (c) 2011 John Stowers
# SPDX-License-Identifier: GPL-3.0+
# License-Filename: LICENSES/GPL-3.0

import logging
from typing import Callable, Optional

from gi.repository import Gtk

from gtweak.tweakmodel import Tweak
from gtweak.widgets import ListBoxTweakGroup, GSettingsSpinButtonTweak, GSettingsFontButtonTweak, ListBoxTweakSubgroup, TweaksCheckGroupActionRow
from gtweak.gsettings import GSettingsSetting

class FontHintingTweak(TweaksCheckGroupActionRow):

    def __init__(self, **options):
        TweaksCheckGroupActionRow.__init__(self,
                             title=_("Hinting"),
                             setting="org.gnome.desktop.interface",
                             key_name="font-hinting"
        )

        self.add_row(title=_("Full"), key_name="full")
        self.add_row(title=_("Medium"), key_name="medium")
        self.add_row(title=_("Slight"), key_name="slight")
        self.add_row(title=_("None"), key_name="none")

class FontAliasingTweak(TweaksCheckGroupActionRow):

    def __init__(self, **options):
        TweaksCheckGroupActionRow.__init__(self,
                             title=_("Antialiasing"),
                             setting="org.gnome.desktop.interface",
                             key_name="font-antialiasing"
        )
      
        self.add_row(title=_("Subpixel (for LCD screens)"), key_name="rgba")
        self.add_row(title=_("Standard (grayscale)"), key_name="grayscale")
        self.add_row(title=_("None"), key_name="none")


TWEAK_GROUP = ListBoxTweakGroup("fonts", _("Fonts"),
                                ListBoxTweakSubgroup(
                                    _("Preferred Fonts"), "preferred-fonts",
    GSettingsFontButtonTweak(_("Interface Text"),"org.gnome.desktop.interface", "font-name"),
    GSettingsFontButtonTweak(_("Document Text"), "org.gnome.desktop.interface", "document-font-name"),
    GSettingsFontButtonTweak(_("Monospace Text"), "org.gnome.desktop.interface", "monospace-font-name"),
    GSettingsFontButtonTweak(_("Legacy Window Titles"),"org.gnome.desktop.wm.preferences", "titlebar-font"),
                                ),
                                 ListBoxTweakSubgroup(
                                     _("Rendering"), "font-rendering",
    FontHintingTweak(),
    FontAliasingTweak(),
                                 ),
                                  ListBoxTweakSubgroup( _("Size"), "font-size",
    GSettingsSpinButtonTweak(_("Scaling Factor"),
      "org.gnome.desktop.interface", "text-scaling-factor",
      adjustment_step=0.01, digits=2),
                                  ),
)

