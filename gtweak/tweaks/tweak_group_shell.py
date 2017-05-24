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

from gi.repository import Gtk, Gio, GLib

import gtweak
from gtweak.gsettings import GSettingsSetting, GSettingsMissingError, GSettingsFakeSetting
from gtweak.gshellwrapper import GnomeShellFactory
from gtweak.tweakmodel import TWEAK_GROUP_TOPBAR, TWEAK_GROUP_WORKSPACES, TWEAK_GROUP_POWER
from gtweak.widgets import ListBoxTweakGroup, GSettingsComboEnumTweak, GSettingsSwitchTweak, GSettingsCheckTweak, GetterSetterSwitchTweak, adjust_schema_for_overrides, build_label_beside_widget, build_horizontal_sizegroup, UI_BOX_SPACING, Title, _GSettingsTweak, build_combo_box_text, GSettingsSpinButtonTweak
from gtweak.utils import XSettingsOverrides, AutostartFile

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

class IgnoreLidSwitchTweak(GetterSetterSwitchTweak):
    def __init__(self, **options):
        self._inhibitor_name = "gnome-tweak-tool-lid-inhibitor"
        self._inhibitor_path = "%s/%s" % (gtweak.LIBEXEC_DIR, self._inhibitor_name)

        self._dfile = AutostartFile(None,
                                    autostart_desktop_filename = "ignore-lid-switch-tweak.desktop",
                                    exec_cmd = self._inhibitor_path)

        GetterSetterSwitchTweak.__init__(self, _("Don't suspend on lid close"), **options)

    def get_active(self):
        return self._sync_inhibitor()

    def set_active(self, v):
        self._dfile.update_start_at_login(v)
        self._sync_inhibitor()

    def _sync_inhibitor(self):
        if (self._dfile.is_start_at_login_enabled()):
            GLib.spawn_command_line_async(self._inhibitor_path)
            return True
        else:
            bus = Gio.bus_get_sync(Gio.BusType.SESSION, None)
            bus.call('org.gnome.tweak-tool.lid-inhibitor',
                     '/org/gnome/tweak_tool/lid_inhibitor',
                     'org.gtk.Actions',
                     'Activate',
                     GLib.Variant('(sava{sv})', ('quit', [], {})),
                     None, 0, -1, None)
            return False

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
        GSettingsCheckTweak(_("Show week numbers"),"org.gnome.desktop.calendar", "show-weekdate", schema_filename="org.gnome.desktop.calendar.gschema.xml"),
    ),
    ListBoxTweakGroup(TWEAK_GROUP_POWER,
        Title(_("When Power Button is Pressed"), "", uid="title-theme"),
        GSettingsComboEnumTweak(_("Action"), "org.gnome.settings-daemon.plugins.power", "power-button-action", size_group=sg),
        Title(_("When Laptop Lid is Closed"), "", uid="title-theme"),
        GSettingsComboEnumTweak(_("On Battery Power"),"org.gnome.settings-daemon.plugins.power", "lid-close-battery-action", size_group=sg),
        GSettingsComboEnumTweak(_("When plugged in"),"org.gnome.settings-daemon.plugins.power", "lid-close-ac-action", size_group=sg),
        GSettingsSwitchTweak(_("Suspend even if an external monitor is plugged in"),"org.gnome.settings-daemon.plugins.power", "lid-close-suspend-with-external-monitor", size_group=sg),
        IgnoreLidSwitchTweak(),
    ),
    ListBoxTweakGroup(TWEAK_GROUP_WORKSPACES,
        sw,
        GSettingsSpinButtonTweak(_("Number of Workspaces"), "org.gnome.desktop.wm.preferences", "num-workspaces", depends_on = sw, depends_how=depends_how, size_group=sg),
        GSettingsSwitchTweak(_("Workspaces only on primary display"),"org.gnome.mutter", "workspaces-only-on-primary", schema_filename="org.gnome.shell.gschema.xml", loaded=_shell_loaded),
    )              
]
