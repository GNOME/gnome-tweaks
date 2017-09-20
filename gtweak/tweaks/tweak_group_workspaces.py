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
from gtweak.gshellwrapper import GnomeShellFactory
from gtweak.tweakmodel import Tweak
from gtweak.widgets import ListBoxTweakGroup, build_horizontal_sizegroup, Title, GSettingsSpinButtonTweak, _GSettingsTweak

_shell = GnomeShellFactory().get_shell()
_shell_loaded = _shell is not None


class StaticWorkspaceTweak(Gtk.ListBox, _GSettingsTweak):

    def __init__(self, **options):
        name = _("Dynamic Workspaces")
        Gtk.ListBox.__init__(self)
        _GSettingsTweak.__init__(self, name, "org.gnome.mutter", "dynamic-workspaces", loaded=_shell_loaded)

        self.set_selection_mode(Gtk.SelectionMode.NONE)

        # Needs other page elements to get margins too
        # self.props.margin_left = 50
        # self.props.margin_right = 50

        row = Gtk.ListBoxRow()
        hbox = Gtk.Box()
        hbox.props.margin = 10
        row.add(hbox)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        lbl = Gtk.Label(name, xalign=0)
        lbl.props.xalign = 0.0
        desc = _("Workspaces can be created on demand, and are automatically removed when empty.")
        lbl_desc = Gtk.Label()
        lbl_desc.set_line_wrap(True)
        lbl_desc.get_style_context().add_class("dim-label")
        lbl_desc.set_markup("<span size='small'>"+GLib.markup_escape_text(desc)+"</span>")

        self.check1 = Gtk.Image.new_from_icon_name("object-select-symbolic", Gtk.IconSize.SMALL_TOOLBAR);
        self.check1.set_no_show_all(True)
        self.check1.set_visible(self.settings[self.key_name])

        vbox.pack_start(lbl, False, False, 0)
        vbox.pack_start(lbl_desc, False, False, 0)
        hbox.pack_start(vbox, False, False, 0)
        hbox.pack_end(self.check1, False, False, 0)

        self.add(row)

        row = Gtk.ListBoxRow()
        hbox = Gtk.Box()
        hbox.props.margin = 10
        row.add(hbox)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        lbl = Gtk.Label(_("Static Workspaces"), xalign=0)
        lbl.props.xalign = 0.0
        desc = _("Number of workspaces is fixed.")
        lbl_desc = Gtk.Label()
        lbl_desc.set_line_wrap(True)
        lbl_desc.get_style_context().add_class("dim-label")
        lbl_desc.set_markup("<span size='small'>"+GLib.markup_escape_text(desc)+"</span>")

        self.check2 = Gtk.Image.new_from_icon_name("object-select-symbolic", Gtk.IconSize.SMALL_TOOLBAR);
        self.check2.set_no_show_all(True)
        self.check2.set_visible(not self.settings[self.key_name])

        vbox.pack_start(lbl, False, False, 0)
        vbox.pack_start(lbl_desc, False, False, 0)
        hbox.pack_start(vbox, False, False, 0)
        hbox.pack_end(self.check2, False, False, 0)

        self.add(row)
        self.connect('row-activated', self.on_row_clicked)

    def on_row_clicked(self, box, row):
        if row.get_index() == 0:
            self.settings[self.key_name] = True
            self.check1.show()
            self.check2.hide()
        else:
            self.settings[self.key_name] = False
            self.check1.hide()
            self.check2.show()

class PrimaryWorkspaceTweak(Gtk.ListBox, Tweak):

    def __init__(self, **options):
        name = _("Workspaces")
        Gtk.ListBox.__init__(self)
        Tweak.__init__(self, _("Display Handling"), _("Workspaces span displays"), loaded=_shell_loaded,)
        _GSettingsTweak.__init__(self, name, "org.gnome.mutter", "workspaces-only-on-primary", loaded=_shell_loaded)

        self.set_selection_mode(Gtk.SelectionMode.NONE)

        # Needs other page elements to get margins too
        # self.props.margin_left = 50
        # self.props.margin_right = 50

        row = Gtk.ListBoxRow()
        hbox = Gtk.Box()
        hbox.props.margin = 10
        row.add(hbox)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        lbl = Gtk.Label(_("Workspaces on primary display only"), xalign=0)
        lbl.props.xalign = 0.0
        desc = _("Additional displays are treated as independent workspaces.")
        lbl_desc = Gtk.Label()
        lbl_desc.set_line_wrap(True)
        lbl_desc.get_style_context().add_class("dim-label")
        lbl_desc.set_markup("<span size='small'>"+GLib.markup_escape_text(desc)+"</span>")

        self.check1 = Gtk.Image.new_from_icon_name("object-select-symbolic", Gtk.IconSize.SMALL_TOOLBAR);
        self.check1.set_no_show_all(True)
        self.check1.set_visible(self.settings[self.key_name])

        vbox.pack_start(lbl, False, False, 0)
        vbox.pack_start(lbl_desc, False, False, 0)
        hbox.pack_start(vbox, False, False, 0)
        hbox.pack_end(self.check1, False, False, 0)

        self.add(row)

        row = Gtk.ListBoxRow()
        hbox = Gtk.Box()
        hbox.props.margin = 10
        row.add(hbox)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        lbl = Gtk.Label(_("Workspaces span displays"), xalign=0)
        lbl.props.xalign = 0.0
        desc = _("The current workspace includes additional displays.")
        lbl_desc = Gtk.Label()
        lbl_desc.set_line_wrap(True)
        lbl_desc.get_style_context().add_class("dim-label")
        lbl_desc.set_markup("<span size='small'>"+GLib.markup_escape_text(desc)+"</span>")

        self.check2 = Gtk.Image.new_from_icon_name("object-select-symbolic", Gtk.IconSize.SMALL_TOOLBAR);
        self.check2.set_no_show_all(True)
        self.check2.set_visible(not self.settings[self.key_name])

        vbox.pack_start(lbl, False, False, 0)
        vbox.pack_start(lbl_desc, False, False, 0)
        hbox.pack_start(vbox, False, False, 0)
        hbox.pack_end(self.check2, False, False, 0)

        self.add(row)
        self.connect('row-activated', self.on_row_clicked)

    def on_row_clicked(self, box, row):
        if row.get_index() == 0:
            self.settings[self.key_name] = True
            self.check1.show()
            self.check2.hide()
        else:
            self.settings[self.key_name] = False
            self.check1.hide()
            self.check2.show()

sg = build_horizontal_sizegroup()
sw = StaticWorkspaceTweak(size_group=sg, loaded=_shell_loaded)
depends_how = lambda x,kn: not(x.get_boolean(kn))

TWEAK_GROUPS = [
    ListBoxTweakGroup(_("Workspaces"),
        sw,
        GSettingsSpinButtonTweak(_("Number of Workspaces"), "org.gnome.desktop.wm.preferences", "num-workspaces", depends_on = sw, depends_how=depends_how, size_group=sg),
        Title(_("Display Handling"), "", uid="title-theme", loaded=_shell_loaded),
        PrimaryWorkspaceTweak(),
    )
]
