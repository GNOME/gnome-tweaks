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
from gtweak.tweakmodel import Tweak, TWEAK_GROUP_TOPBAR, TWEAK_GROUP_WORKSPACES, TWEAK_GROUP_POWER
from gtweak.widgets import ListBoxTweakGroup, GSettingsComboEnumTweak, GSettingsSwitchTweak, GSettingsCheckTweak, GetterSetterSwitchTweak, adjust_schema_for_overrides, build_label_beside_widget, build_horizontal_sizegroup, UI_BOX_SPACING, Title
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

class StaticWorkspaceTweak(Gtk.Box, Tweak):

    NUM_WORKSPACES_SCHEMA = "org.gnome.desktop.wm.preferences"
    NUM_WORKSPACES_KEY = "num-workspaces"

    DYNAMIC_KEY = "dynamic-workspaces"
    DYNAMIC_SCHEMA = "org.gnome.mutter"

    def __init__(self, **options):
        schema = adjust_schema_for_overrides(self.DYNAMIC_SCHEMA, self.DYNAMIC_KEY, options)
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.HORIZONTAL)
        Tweak.__init__(self, _("Dynamic workspaces"), _("Disable gnome-shell dynamic workspace management, use static workspaces"), **options)

        try:
            nwsettings = GSettingsSetting(self.NUM_WORKSPACES_SCHEMA, **options)
        except GSettingsMissingError:
            self.loaded = False
            nwsettings = GSettingsFakeSetting()

        try:
            dsettings = GSettingsSetting(schema, **options)
        except GSettingsMissingError:
            self.loaded = False
            dsettings = GSettingsFakeSetting()

        adj = Gtk.Adjustment(1, 1, 99, 1)
        sb = Gtk.SpinButton(adjustment=adj, digits=0)
        nwsettings.bind(self.NUM_WORKSPACES_KEY, adj, "value", Gio.SettingsBindFlags.DEFAULT)

        sw = Gtk.Switch()
        dsettings.bind(self.DYNAMIC_KEY, sw, "active", Gio.SettingsBindFlags.DEFAULT)
        #sw.bind_property ("active", sb, "sensitive", GObject.BindingFlags.SYNC_CREATE)
        sb.set_sensitive(not dsettings[self.DYNAMIC_KEY])
        sw.connect('notify::active', lambda _sw,_param,_sb: _sb.set_sensitive(not _sw.get_active()), sb)

        hb = Gtk.HBox(spacing=UI_BOX_SPACING)
        hb.pack_start(sw, False, False, 0)
        hb.pack_start(sb, True, True, 0)

        build_label_beside_widget(self.name, hb, hbox=self)
        self.widget_for_size_group = hb

sg = build_horizontal_sizegroup()

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
        StaticWorkspaceTweak(size_group=sg, loaded=_shell_loaded),
        GSettingsSwitchTweak(_("Workspaces only on primary display"),"org.gnome.mutter", "workspaces-only-on-primary", schema_filename="org.gnome.shell.gschema.xml", loaded=_shell_loaded),
    )              
]
