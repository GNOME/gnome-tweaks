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

from gtweak.widgets import ListBoxTweakGroup, GSettingsSwitchTweak, GSettingsComboEnumTweak, GSettingsFileChooserButtonTweak, GSettingsCheckTweak, Title

dicons = GSettingsSwitchTweak(_("Icons on Desktop"),"org.gnome.desktop.background","show-desktop-icons")

TWEAK_GROUPS = [
    ListBoxTweakGroup(_("Desktop"),
        dicons,
        GSettingsCheckTweak(_("Computer"),"org.gnome.nautilus.desktop", "computer-icon-visible", depends_on=dicons, schema_filename="org.gnome.nautilus.gschema.xml"),
        GSettingsCheckTweak(_("Home"),"org.gnome.nautilus.desktop", "home-icon-visible", depends_on=dicons, schema_filename="org.gnome.nautilus.gschema.xml"),
        GSettingsCheckTweak(_("Network Servers"),"org.gnome.nautilus.desktop", "network-icon-visible", depends_on=dicons, schema_filename="org.gnome.nautilus.gschema.xml"),
        GSettingsCheckTweak(_("Trash"),"org.gnome.nautilus.desktop", "trash-icon-visible", depends_on=dicons, schema_filename="org.gnome.nautilus.gschema.xml"),
        GSettingsCheckTweak(_("Mounted Volumes"),"org.gnome.nautilus.desktop", "volumes-visible", depends_on=dicons, schema_filename="org.gnome.nautilus.gschema.xml"),
        Title(_("Background"), "", uid="title-theme"),
        GSettingsComboEnumTweak(_("Mode"),"org.gnome.desktop.background", "picture-options"),
        GSettingsFileChooserButtonTweak(_("Background Location"),"org.gnome.desktop.background", "picture-uri", local_only=True, mimetypes=["application/xml","image/png","image/jpeg"]),
        #Title(_("Files"), ""),
        #GSettingsSwitchTweak(_("Use location entry"), "org.gnome.nautilus.preferences", "always-use-location-entry",schema_filename="org.gnome.nautilus.gschema.xml"),

    )
]
