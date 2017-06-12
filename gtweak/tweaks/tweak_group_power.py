# This Python file uses the following encoding: utf-8
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

from gi.repository import Gio, GLib, Gtk

import gtweak
from gtweak.tweakmodel import Tweak
from gtweak.widgets import ListBoxTweakGroup, GetterSetterSwitchTweak, build_horizontal_sizegroup, Title
from gtweak.utils import AutostartFile


class IgnoreLidSwitchTweak(GetterSetterSwitchTweak):
    def __init__(self, **options):
        self._inhibitor_name = "gnome-tweak-tool-lid-inhibitor"
        self._inhibitor_path = "%s/%s" % (gtweak.LIBEXEC_DIR, self._inhibitor_name)

        self._dfile = AutostartFile(None,
                                    autostart_desktop_filename = "ignore-lid-switch-tweak.desktop",
                                    exec_cmd = self._inhibitor_path)

        GetterSetterSwitchTweak.__init__(self, _("Suspend when laptop lid is closed"), **options)

    def get_active(self):
        return not self._sync_inhibitor()

    def set_active(self, v):
        self._dfile.update_start_at_login(not v)
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


class PowerButtonTweak(Gtk.ListBox, Tweak):

    def __init__(self, **options):
        Gtk.ListBox.__init__(self)
        Tweak.__init__(self, _("Power Button Behavior"), "")

        self.settings = Gio.Settings("org.gnome.settings-daemon.plugins.power")
        self.key_name = "power-button-action"

        self.set_selection_mode(Gtk.SelectionMode.NONE)

        # Needs other page elements to get margins too
        # self.props.margin_left = 50
        # self.props.margin_right = 50

        row = Gtk.ListBoxRow()
        hbox = Gtk.Box()
        hbox.props.margin = 10
        row.add(hbox)

        lbl = Gtk.Label(_("Suspend"), xalign=0)
        lbl.props.xalign = 0.0

        self.check_suspend = Gtk.Image.new_from_icon_name("object-select-symbolic", Gtk.IconSize.SMALL_TOOLBAR);
        self.check_suspend.set_no_show_all(True)
        self.check_suspend.set_visible(self.settings[self.key_name] == "suspend")

        hbox.pack_start(lbl, False, False, 0)
        hbox.pack_end(self.check_suspend, False, False, 0)

        self.add(row)

        row = Gtk.ListBoxRow()
        hbox = Gtk.Box()
        hbox.props.margin = 10
        row.add(hbox)

        lbl = Gtk.Label(_("Hibernate"), xalign=0)
        lbl.props.xalign = 0.0

        self.check_hibernate = Gtk.Image.new_from_icon_name("object-select-symbolic", Gtk.IconSize.SMALL_TOOLBAR);
        self.check_hibernate.set_no_show_all(True)
        self.check_hibernate.set_visible(self.settings[self.key_name] == "hibernate")

        hbox.pack_start(lbl, False, False, 0)
        hbox.pack_end(self.check_hibernate, False, False, 0)

        self.add(row)

        row = Gtk.ListBoxRow()
        hbox = Gtk.Box()
        hbox.props.margin = 10
        row.add(hbox)

        lbl = Gtk.Label(_("Power Off"), xalign=0)
        lbl.props.xalign = 0.0

        self.check_poweroff = Gtk.Image.new_from_icon_name("object-select-symbolic", Gtk.IconSize.SMALL_TOOLBAR);
        self.check_poweroff.set_no_show_all(True)
        self.check_poweroff.set_visible(self.settings[self.key_name] == "interactive" or self.settings[self.key_name] == "shutdown")

        hbox.pack_start(lbl, False, False, 0)
        hbox.pack_end(self.check_poweroff, False, False, 0)

        # Distros that have re-enabled the "interactive" option can uncomment this:
        # self.add(row)

        row = Gtk.ListBoxRow()
        hbox = Gtk.Box()
        hbox.props.margin = 10
        row.add(hbox)

        lbl = Gtk.Label(_("No Action"), xalign=0)
        lbl.props.xalign = 0.0

        self.check_noaction = Gtk.Image.new_from_icon_name("object-select-symbolic", Gtk.IconSize.SMALL_TOOLBAR);
        self.check_noaction.set_no_show_all(True)
        self.check_noaction.set_visible(self.settings[self.key_name] == "nothing")

        hbox.pack_start(lbl, False, False, 0)
        hbox.pack_end(self.check_noaction, False, False, 0)

        self.add(row)

        self.connect('row-activated', self.on_row_clicked)

    def on_row_clicked(self, box, row):
        if row.get_index() == 0:
            self.settings[self.key_name] = "suspend"
            self.check_suspend.show()
            self.check_hibernate.hide()
            self.check_poweroff.hide()
            self.check_noaction.hide()
        elif row.get_index() == 1:
            self.settings[self.key_name] = "hibernate"
            self.check_suspend.hide()
            self.check_hibernate.show()
            self.check_poweroff.hide()
            self.check_noaction.hide()
        elif row.get_index() == 2:
            self.settings[self.key_name] = "interactive"
            self.check_suspend.hide()
            self.check_hibernate.hide()
            self.check_poweroff.show()
            self.check_noaction.hide()
        else:
            self.settings[self.key_name] = "nothing"
            self.check_suspend.hide()
            self.check_hibernate.hide()
            self.check_poweroff.hide()
            self.check_noaction.show()

sg = build_horizontal_sizegroup()

TWEAK_GROUPS = [
    ListBoxTweakGroup(_("Power"),
        IgnoreLidSwitchTweak(),
        Title(_("Power Button Behavior"), "", uid="title-theme"),
        PowerButtonTweak(),
    ),
]
