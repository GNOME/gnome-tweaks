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

from gi.repository import Gtk

import gtweak
from gtweak.gsettings import GSettingsSetting, GSettingsMissingError, GSettingsFakeSetting
from gtweak.gshellwrapper import GnomeShellFactory
from gtweak.widgets import ListBoxTweakGroup, GSettingsSwitchTweak, build_label_beside_widget, build_horizontal_sizegroup, Title, _GSettingsTweak, build_combo_box_text, GSettingsSpinButtonTweak

_shell = GnomeShellFactory().get_shell()
_shell_loaded = _shell is not None

class StaticWorkspaceTweak(Gtk.Box, _GSettingsTweak):

    STATUS = {'dynamic':True, 'static': False}

    def __init__(self, **options):
        name = _("Workspace Creation")
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.HORIZONTAL)
        _GSettingsTweak.__init__(self, name, "org.gnome.mutter", "dynamic-workspaces", **options)

        default = list(self.STATUS.keys())[list(self.STATUS.values()).index(self.settings[self.key_name])]
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
    ListBoxTweakGroup(_("Workspaces"),
        sw,
        GSettingsSpinButtonTweak(_("Number of Workspaces"), "org.gnome.desktop.wm.preferences", "num-workspaces", depends_on = sw, depends_how=depends_how, size_group=sg),
        Title(_("Display Handling"), "", uid="title-theme"),
        GSettingsSwitchTweak(_("Workspaces on primary display only"),"org.gnome.mutter", "workspaces-only-on-primary", schema_filename="org.gnome.shell.gschema.xml", desc=_("Additional displays are treated as independent workspaces."),loaded=_shell_loaded),
    )
]
