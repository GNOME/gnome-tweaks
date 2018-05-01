# Copyright (c) 2011 John Stowers
# SPDX-License-Identifier: GPL-3.0+
# License-Filename: LICENSES/GPL-3.0

import gtweak
from gtweak.tweakmodel import Tweak
from gtweak.widgets import ListBoxTweakGroup, GSettingsComboEnumTweak, Title, GSettingsSwitchTweakValue, build_label_beside_widget, _GSettingsTweak

from gi.repository import Gtk


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


TWEAK_GROUPS = [
    ListBoxTweakGroup(_("Window Titlebars"),
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

