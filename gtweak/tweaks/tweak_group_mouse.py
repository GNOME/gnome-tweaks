# Copyright (c) 2011 John Stowers
# SPDX-License-Identifier: GPL-3.0+
# License-Filename: LICENSES/GPL-3.0

from gi.repository import GDesktopEnums
from gtweak.devicemanager import pointing_stick_is_present, touchpad_is_present

from gtweak.widgets import (GSettingsTweakComboRow, TweakPreferencesPage, GSettingsTweakSwitchRow, GSettingsSwitchTweakValue, TweakPreferencesGroup)

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


class PointerAccelProfile(GSettingsSwitchTweakValue):

    def __init__(self, title, description, peripheral_type, **options):
        GSettingsSwitchTweakValue.__init__(self,
                                           title=title,
                                           schema_name="org.gnome.desktop.peripherals",
                                           schema_id=f"org.gnome.desktop.peripherals.{peripheral_type}",
                                           schema_child_name=peripheral_type,
                                           key_name="accel-profile",
                                           desc=description,
                                           **options)

    def get_active(self):
        return self.settings.get_enum(self.key_name) != GDesktopEnums.PointerAccelProfile.FLAT
    
    def set_active(self, v):
        if not v:
          self.settings.set_enum(self.key_name, GDesktopEnums.PointerAccelProfile.FLAT)
        else:
          self.settings.reset(self.key_name)


_tweaks = [
  TweakPreferencesGroup(_("Mouse"), "mouse",
    GSettingsTweakSwitchRow(_("Middle Click Paste"),
                         "org.gnome.desktop.interface",
                         "gtk-enable-primary-paste"),
  ),
]

if touchpad_is_present():
  _tweaks += [
    TweakPreferencesGroup(_("Touchpad"), "touchpad",
      PointerAccelProfile(
        title=_("Touchpad Acceleration"),
        description=_("Turning acceleration off can allow faster and more precise movements, but can also make the touchpad more difficult to use."),
        peripheral_type="touchpad",
      ),
      ClickMethod(),
    ),
  ]

if pointing_stick_is_present():
  _tweaks += [
    TweakPreferencesGroup(_("Pointing Stick"), "pointing-stick",
      PointerAccelProfile(
          title=_("Pointing Stick Acceleration"),
          description=_("Turning acceleration off can allow faster and more precise movements, but can also make the pointing stick more difficult to use."),
          peripheral_type="pointingstick",
      ),
      GSettingsTweakComboRow(
          title=_("Scrolling Method"),
          schema_name="org.gnome.desktop.peripherals",
          schema_child_name="pointingstick",
          schema_id="org.gnome.desktop.peripherals.pointingstick",
          key_name="scroll-method",
      ),
    ),
  ]

TWEAK_GROUP = TweakPreferencesPage("mouse", _("Mouse & Touchpad"), *_tweaks)