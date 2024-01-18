# Copyright (c) 2011 John Stowers
# SPDX-License-Identifier: GPL-3.0+
# License-Filename: LICENSES/GPL-3.0

from gtweak.widgets import UI_BOX_HORIZONTAL_SPACING, UI_BOX_SPACING, _GSettingsTweak, GSettingsSwitchTweakValue, TweakPreferencesPage, GSettingsTweakComboRow, GSettingsTweakSwitchRow, TweakPreferencesGroup, TweaksCheckGroupActionRow, build_label_beside_widget

from gi.repository import Gtk


class Focus(TweaksCheckGroupActionRow):

    def __init__(self):
        name: str = _("Window Focus")
        desc: str = _("Click to Focus")
        TweaksCheckGroupActionRow.__init__(self, title=name, subtitle=desc, setting="org.gnome.desktop.wm.preferences", key_name="focus-mode", name="focus")

        self.add_row(
            key_name="click", title=_("Click to Focus"),
            subtitle=_(
                "Windows are focused when they are clicked."))

        self.add_row(
            key_name="sloppy", title=_("Focus on Hover"),
            subtitle=_(
                "Window is focused when hovered with the pointer. Windows remain focused when the desktop is hovered."))

        self.add_row(
            key_name="mouse", title=_("Focus Follows Mouse"),
            subtitle=_(
                "Window is focused when hovered with the pointer. Hovering the desktop removes focus "
                "from the previous window."))


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


TWEAK_GROUP = TweakPreferencesPage(
    "window-management", _("Windows"),
    TweakPreferencesGroup(
        _("Titlebar Actions"), "title-titlebar-actions",
        GSettingsTweakComboRow(_("Double-Click"),"org.gnome.desktop.wm.preferences", "action-double-click-titlebar"),
        GSettingsTweakComboRow(_("Middle-Click"),"org.gnome.desktop.wm.preferences", "action-middle-click-titlebar"),
        GSettingsTweakComboRow(_("Secondary-Click"),"org.gnome.desktop.wm.preferences", "action-right-click-titlebar"),
    ), 
    TweakPreferencesGroup(_("Titlebar Buttons"), "title-theme",
        ShowWindowButtons(_("Maximize"), "maximize"),
        ShowWindowButtons(_("Minimize"), "minimize"),
        PlaceWindowButtons()
    ),
    TweakPreferencesGroup(
        _("Click Actions"), "title-window-behavior",
        GSettingsTweakSwitchRow(_("Attach Modal Dialogs"),"org.gnome.mutter", "attach-modal-dialogs",
                        desc=_("When on, modal dialog windows are attached to their parent windows, and cannot be moved.")),
        GSettingsTweakSwitchRow(_("Center New Windows"),"org.gnome.mutter", "center-new-windows"),
        GSettingsTweakComboRow(_("Window Action Key"),
                        "org.gnome.desktop.wm.preferences",
                        "mouse-button-modifier",
                        [("disabled", _("Disabled")), ("<Alt>", "Alt"), ("<Super>", "Super")]),
  
    
        GSettingsTweakSwitchRow(_("Resize with Secondary-Click"),"org.gnome.desktop.wm.preferences", "resize-with-right-button"),
     ),
 
 TweakPreferencesGroup(_("Window Focus"), "window-focus", 
                       Focus(),
                      GSettingsTweakSwitchRow(_("Raise Windows When Focused"),"org.gnome.desktop.wm.preferences", "auto-raise", depends_on=Focus(), depends_how=depends_how))
)    

