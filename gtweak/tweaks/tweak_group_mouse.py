# Copyright (c) 2011 John Stowers
# SPDX-License-Identifier: GPL-3.0+
# License-Filename: LICENSES/GPL-3.0

from gi.repository import GDesktopEnums

from gtweak.widgets import (TweakPreferencesPage, GSettingsTweakSwitchRow, GSettingsSwitchTweakValue, TweakPreferencesGroup)

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

class ClickMethod(GSettingsSwitchTweakValue):

    def __init__(self, **options):
        title = _("Disable Secondary Click")
        desc = _("Disables secondary clicks on touchpads which do not have a physical secondary button")

        GSettingsSwitchTweakValue.__init__(self,
                                           title=title,
                                           schema_name="org.gnome.desktop.peripherals",
                                           schema_child_name="touchpad",
                                           schema_id="org.gnome.desktop.peripherals.touchpad",
                                           key_name="click-method",
                                           desc=desc,
                                           **options)

    def get_active(self):
        return self.settings.get_enum(self.key_name) == GDesktopEnums.TouchpadClickMethod.NONE
    
    def set_active(self, v):
        if v:
          self.settings.set_enum(self.key_name, GDesktopEnums.TouchpadClickMethod.NONE)
        else:
          self.settings.reset(self.key_name)


TWEAK_GROUP = TweakPreferencesPage("mouse", _("Mouse & Touchpad"),
  TweakPreferencesGroup(_("Mouse"), "mouse",
    GSettingsTweakSwitchRow(_("Middle Click Paste"),
                         "org.gnome.desktop.interface",
                         "gtk-enable-primary-paste"),
  ),
  TweakPreferencesGroup(_("Touchpad"), "touchpad",
    ClickMethod(),
  ),
)
