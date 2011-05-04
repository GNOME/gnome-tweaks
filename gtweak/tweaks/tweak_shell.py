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

import os.path
import shutil
import zipfile
import tempfile
import logging

from gi.repository import Gtk
from gi.repository import GLib

from gtweak.utils import walk_directories
from gtweak.gsettings import GSettingsSetting
from gtweak.gshellwrapper import GnomeShell
from gtweak.tweakmodel import Tweak, TweakGroup
from gtweak.widgets import GConfComboTweak, GSettingsComboEnumTweak, GSettingsSwitchTweak, build_label_beside_widget, build_horizontal_sizegroup, build_combo_box_text

class ShowWindowButtons(GConfComboTweak):
    def __init__(self, **options):
        GConfComboTweak.__init__(self,
            "/desktop/gnome/shell/windows/button_layout",
            str,
            ((':close', 'Close Only'),
            (':minimize,close', 'Minimize and Close'),
            (':maximize,close', 'Maximize and Close'),
            (':minimize,maximize,close', 'All')),
            **options)

class _ThemeZipChooser(Gtk.FileChooserButton):
    def __init__(self):
        Gtk.FileChooserButton.__init__(self, title="Select theme file")

        f = Gtk.FileFilter()
        f.add_mime_type("application/zip")
        self.set_filter(f)

        #self.set_width_chars(15)
        self.set_local_only(True)

class ShellThemeTweak(Tweak):

    THEME_EXT_NAME = "user-theme@gnome-shell-extensions.gnome.org"
    THEME_GSETTINGS_SCHEMA = "org.gnome.shell.extensions.user-theme"
    THEME_GSETTINGS_NAME = "name"
    THEME_DIR = os.path.join(GLib.get_home_dir(), ".themes")

    def __init__(self, **options):
        Tweak.__init__(self, "Shell theme", "Install custom or user themes for gnome-shell", **options)

        #check the shell is running and the usertheme extension is present
        error = "Unknown"
        try:
            self._shell = GnomeShell()
        except:
            error = "Shell not running"
        try:
            extensions = self._shell.list_extensions()
            if ShellThemeTweak.THEME_EXT_NAME in extensions and extensions[ShellThemeTweak.THEME_EXT_NAME]["state"] == 1:
                #check the correct gsettings key is present
                try:
                    self._settings = GSettingsSetting(ShellThemeTweak.THEME_GSETTINGS_SCHEMA)
                    name = self._settings.get_value(ShellThemeTweak.THEME_GSETTINGS_NAME)

                    #assume the usertheme version is that version of the shell which
                    #it most supports (this is a poor assumption)
                    self._usertheme_extension_version = max(extensions[ShellThemeTweak.THEME_EXT_NAME]["shell-version"])

                    error = None
                except:
                    error = "User Theme extension schema missing"

            else:
                error = "User Theme extension not enabled"
        except Exception, e:
            error = "Could not list shell extensions"

        if error:
            info = Gtk.InfoBar()
            info.props.message_type = Gtk.MessageType.INFO
            info.get_content_area().add(Gtk.Label(error))
            self.widget = build_label_beside_widget(self.name, info)
            self.widget_for_size_group = info
        else:
            hb = Gtk.HBox()

            #include both system, and user themes
            #note: the default theme lives in /system/data/dir/gnome-shell/theme
            #      and not themes/, so add it manually later
            dirs = [os.path.join(d, "themes") for d in GLib.get_system_data_dirs()]
            dirs += [ShellThemeTweak.THEME_DIR]

            valid = walk_directories(dirs, lambda d:
                        os.path.exists(os.path.join(d, "gnome-shell")) and \
                        os.path.exists(os.path.join(d, "gnome-shell", "gnome-shell.css")))

            #build a combo box with all the valid theme options
            #manually add Adwiata to represent the default
            cb = build_combo_box_text(
                    self._settings.get_string(ShellThemeTweak.THEME_GSETTINGS_NAME),
                    ("", "Adwiata"),
                    *[(v,v) for v in valid])
            cb.connect('changed', self._on_combo_changed)
            hb.pack_start(cb, False, False, 5)
            self.combo = cb

            chooser = _ThemeZipChooser()
            chooser.connect("file-set", self._on_file_set)
            hb.pack_start(chooser, False, False, 0)

            self.widget = build_label_beside_widget(self.name, hb)
            self.widget_for_size_group = chooser
    
    def _extract_theme_zip(self, z, theme_name, theme_members_path):
        tmp = tempfile.mkdtemp()
        dest = os.path.join(ShellThemeTweak.THEME_DIR, theme_name, "gnome-shell")

        logging.info("Extracting theme %s to %s" % (theme_name, tmp))

        try:
            if os.path.exists(dest):
                shutil.rmtree(dest)
            z.extractall(tmp)
            shutil.copytree(os.path.join(tmp, theme_members_path), dest)
            return theme_name
        except OSError:
            self.notify_error("Error installing theme")
            return None

    def _on_file_set(self, chooser):
        f = chooser.get_filename()

        with zipfile.ZipFile(f, 'r') as z:
            try:
                fragment = ()
                for n in z.namelist():
                    if n.endswith("gnome-shell.css"):
                        fragment = n.split("/")[0:-1]
                        break

                if not fragment:
                    raise Exception("Could not find gnome-shell.css")

                #old style themes name was taken from the zip name
                if fragment[0] == "theme" and len(fragment) == 1:
                    theme_name = os.path.basename(f)
                else:
                    theme_name = fragment[0]
                theme_members_path = "/".join(fragment)

                installed_name = self._extract_theme_zip(
                                        z,
                                        theme_name,
                                        theme_members_path)
                if installed_name:
                    print self.combo.get_model().append( (installed_name, installed_name) )
                    self.notify_info("Installed %s theme successfully" % installed_name)

            except:
                #does not look like a valid theme
                self.notify_error("Invalid theme file")
        #set button back to default state
        chooser.unselect_all()

    def _on_combo_changed(self, combo):
        val = combo.get_model().get_value(combo.get_active_iter(), 0)
        self._settings.set_value(ShellThemeTweak.THEME_GSETTINGS_NAME, val)

        #reloading the theme is not really necessary, the user-theme should pick
        #pick up the change.
        #
        #however there are some problems with reloading images.
        #https://bugzilla.gnome.org/show_bug.cgi?id=644125
        #
        #resetting to the default theme is also fucked
        #https://bugzilla.gnome.org/show_bug.cgi?id=647386
        if not val:
            if self._usertheme_extension_version < "3.0.2":
                self.notify_action_required(
                    "The shell must be restarted to apply the theme",
                    "Restart",
                    lambda: self._shell.restart())

sg = build_horizontal_sizegroup()

TWEAK_GROUPS = (
        TweakGroup(
            "Shell",
            GSettingsSwitchTweak("org.gnome.shell.clock", "show-date", schema_filename="org.gnome.shell.gschema.xml"),
            GSettingsSwitchTweak("org.gnome.shell.calendar", "show-weekdate", schema_filename="org.gnome.shell.gschema.xml"),
            ShowWindowButtons(size_group=sg),
            ShellThemeTweak(size_group=sg),
            GSettingsComboEnumTweak("org.gnome.settings-daemon.plugins.power", "lid-close-battery-action", size_group=sg),
            GSettingsComboEnumTweak("org.gnome.settings-daemon.plugins.power", "lid-close-ac-action", size_group=sg)),
)
