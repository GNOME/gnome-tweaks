# This file is part of gnome-tweak-tool.
#
# Copyright (c) 2011 John Stowers
#
# gnome-tweak-tool is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# gnome-tweak-tool is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with gnome-tweak-tool.  If not, see <http://www.gnu.org/licenses/>.

from gi.repository import Gtk, Gio

from gtweak.gsettings import GSettingsSetting, GSettingsMissingError, GSettingsFakeSetting
from gtweak.gshellwrapper import GnomeShellFactory
from gtweak.tweakmodel import TWEAK_GROUP_TOPBAR, TWEAK_GROUP_WORKSPACES, TWEAK_GROUP_POWER
from gtweak.widgets import ListBoxTweakGroup, GSettingsComboEnumTweak, GSettingsSwitchTweak, GSettingsCheckTweak, GetterSetterSwitchTweak, adjust_schema_for_overrides, build_label_beside_widget, build_horizontal_sizegroup, UI_BOX_SPACING, Title, _GSettingsTweak, build_combo_box_text, GSettingsSpinButtonTweak
from gtweak.utils import XSettingsOverrides

_shell = GnomeShellFactory().get_shell()
_shell_loaded = _shell is not None

class ApplicationMenuTweak(GetterSetterSwitchTweak):
    def __init__(self, **options):
        self._xsettings = XSettingsOverrides()
        GetterSetterSwitchTweak.__init__(self, _("Show Application Menu"), **options)

    def get_active(self):
        return self._xsettings.get_shell_shows_app_menu()

    def set_active(self, v):
        self._xsettings.set_shell_shows_app_menu(v)

class StaticWorkspaceTweak(Gtk.Box, _GSettingsTweak):
    
    STATUS = {'dynamic':True, 'static': False} 

    def __init__(self, **options):
        name = _("Workspace Creation")
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.HORIZONTAL)
        _GSettingsTweak.__init__(self, name, "org.gnome.mutter", "dynamic-workspaces", **options)

        default = self.STATUS.keys()[self.STATUS.values().index(self.settings[self.key_name])]
        key_options = [("dynamic", _("Dynamic")), ("static", _("Static"))]

        self.combo = build_combo_box_text(default, *key_options)
        self.combo.connect('changed', self._on_combo_changed)
        build_label_beside_widget(name, self.combo, hbox=self)
        self.widget_for_size_group = self.combo

    def _on_combo_changed(self, combo):
        _iter = combo.get_active_iter()
        if _iter:
            value = combo.get_model().get_value(_iter, 0)
            val = self.STATUS[value]
            self.settings[self.key_name] = val
        
sg = build_horizontal_sizegroup()
sw = StaticWorkspaceTweak(size_group=sg, loaded=_shell_loaded)
depends_how = lambda x,kn: not(x.get_boolean(kn))

TWEAK_GROUPS = [
    ListBoxTweakGroup(TWEAK_GROUP_TOPBAR,
        ApplicationMenuTweak(),
        Title(_("Clock"),""),
        GSettingsCheckTweak(_("Show date"),"org.gnome.desktop.interface", "clock-show-date", schema_filename="org.gnome.desktop.interface.gschema.xml"),
        GSettingsCheckTweak(_("Show seconds"), "org.gnome.desktop.interface", "clock-show-seconds", schema_filename="org.gnome.desktop.interface.gschema.xml"),
        Title(_("Calendar"),""),
        GSettingsCheckTweak(_("Show week numbers"),"org.gnome.shell.calendar", "show-weekdate", schema_filename="org.gnome.shell.gschema.xml", loaded=_shell_loaded),
    ),
    ListBoxTweakGroup(TWEAK_GROUP_POWER,
        GSettingsComboEnumTweak(_("Power Button Action"), "org.gnome.settings-daemon.plugins.power", "button-power", size_group=sg),
        Title(_("When Laptop Lid is Closed"), "", uid="title-theme"),
        GSettingsComboEnumTweak(_("On Battery Power"),"org.gnome.settings-daemon.plugins.power", "lid-close-battery-action", size_group=sg),
        GSettingsComboEnumTweak(_("When plugged in"),"org.gnome.settings-daemon.plugins.power", "lid-close-ac-action", size_group=sg),
        GSettingsSwitchTweak(_("Suspend even if an external monitor is plugged in"),"org.gnome.settings-daemon.plugins.power", "lid-close-suspend-with-external-monitor", size_group=sg),
    ),
    ListBoxTweakGroup(TWEAK_GROUP_WORKSPACES,
        sw,
        GSettingsSpinButtonTweak(_("Number of Workspaces"), "org.gnome.desktop.wm.preferences", "num-workspaces", depends_on = sw, depends_how=depends_how, size_group=sg),
        GSettingsSwitchTweak(_("Workspaces only on primary display"),"org.gnome.mutter", "workspaces-only-on-primary", schema_filename="org.gnome.shell.gschema.xml", loaded=_shell_loaded),
    )              
]
