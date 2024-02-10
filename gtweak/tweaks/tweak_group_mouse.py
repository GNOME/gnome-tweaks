# Copyright (c) 2011 John Stowers
# SPDX-License-Identifier: GPL-3.0+
# License-Filename: LICENSES/GPL-3.0



from gtweak.widgets import (TweakPreferencesPage, GSettingsTweakSwitchRow, GSettingsSwitchTweakValue, TweakPreferencesGroup,
                           TweaksCheckGroupActionRow)


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

class ClickMethod(TweaksCheckGroupActionRow):

    def __init__(self, **options):
        title = _("Mouse Click Emulation")

        TweaksCheckGroupActionRow.__init__(self, title=title, setting="org.gnome.desktop.peripherals.touchpad", key_name="click-method", **options)

        self.add_row(
            key_name="fingers", title=_("Fingers"),
            subtitle=_(
                "Click the touchpad with two fingers for right-click and three fingers for middle-click."))

        self.add_row(
            key_name="areas", title=_("Area"),
            subtitle=_(
                "Click the bottom right of the touchpad for right-click and the bottom middle for middle-click."))

        self.add_row(
            key_name="none", title=_("Disabled"),
            subtitle=_(
                "Don’t use mouse click emulation."))


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
