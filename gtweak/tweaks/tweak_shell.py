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
import zipfile
import tempfile
import logging
import json

from gi.repository import Gtk
from gi.repository import GLib

from gtweak.utils import walk_directories, extract_zip_file, make_combo_list_with_default
from gtweak.gsettings import GSettingsSetting
from gtweak.gshellwrapper import GnomeShell
from gtweak.tweakmodel import Tweak, TweakGroup
from gtweak.widgets import ZipFileChooserButton, GConfComboTweak, GSettingsComboEnumTweak, GSettingsSwitchTweak, build_label_beside_widget, build_horizontal_sizegroup, build_combo_box_text

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

class ShellThemeTweak(Tweak):

    THEME_EXT_NAME = "user-theme@gnome-shell-extensions.gnome.org"
    THEME_GSETTINGS_SCHEMA = "org.gnome.shell.extensions.user-theme"
    THEME_GSETTINGS_NAME = "name"
    THEME_DIR = os.path.join(GLib.get_home_dir(), ".themes")

    def __init__(self, **options):
        Tweak.__init__(self, "Shell Theme", "Install custom or user themes for gnome-shell", **options)

        #check the shell is running and the usertheme extension is present
        error = _("Unknown error")
        try:
            self._shell = GnomeShell()
        except:
            error = _("Shell not running")
        try:
            extensions = self._shell.list_extensions()
            if ShellThemeTweak.THEME_EXT_NAME in extensions and extensions[ShellThemeTweak.THEME_EXT_NAME]["state"] == 1:
                #check the correct gsettings key is present
                try:
                    self._settings = GSettingsSetting(ShellThemeTweak.THEME_GSETTINGS_SCHEMA)
                    name = self._settings.get_string(ShellThemeTweak.THEME_GSETTINGS_NAME)

                    #assume the usertheme version is that version of the shell which
                    #it most supports (this is a poor assumption)
                    self._usertheme_extension_version = max(extensions[ShellThemeTweak.THEME_EXT_NAME]["shell-version"])
                    logging.info("Shell user-theme extension v%s", self._usertheme_extension_version)

                    error = None
                except:
                    error = _("Shell user-theme extension incorrectly installed")

            else:
                error = _("Shell user-theme extension not enabled")
        except Exception, e:
            error = _("Could not list shell extensions")

        if error:
            cb = build_combo_box_text(None)
            self.widget = build_label_beside_widget(self.name, cb, warning=error)
            self.widget_for_size_group = cb
        else:
            #include both system, and user themes
            #note: the default theme lives in /system/data/dir/gnome-shell/theme
            #      and not themes/, so add it manually later
            dirs = [os.path.join(d, "themes") for d in GLib.get_system_data_dirs()]
            dirs += [ShellThemeTweak.THEME_DIR]

            valid = walk_directories(dirs, lambda d:
                        os.path.exists(os.path.join(d, "gnome-shell")) and \
                        os.path.exists(os.path.join(d, "gnome-shell", "gnome-shell.css")))
            #the default value to reset the shell is an empty string
            valid.extend( ("",) )

            #build a combo box with all the valid theme options
            #manually add Adwaita to represent the default
            cb = build_combo_box_text(
                    self._settings.get_string(ShellThemeTweak.THEME_GSETTINGS_NAME),
                    *make_combo_list_with_default(
                        valid,
                        "",
                        default_text=_("<i>Default</i>")))
            cb.connect('changed', self._on_combo_changed)
            self._combo = cb

            #a filechooser to install new themes
            chooser = ZipFileChooserButton(_("Select a theme"))
            chooser.connect("file-set", self._on_file_set)

            self.widget = build_label_beside_widget(self.name, chooser, cb)
            self.widget_for_size_group = cb
    
    def _on_file_set(self, chooser):
        f = chooser.get_filename()

        with zipfile.ZipFile(f, 'r') as z:
            try:
                fragment = ()
                theme_name = None
                for n in z.namelist():
                    if n.endswith("gnome-shell.css"):
                        fragment = n.split("/")[0:-1]
                    if n.endswith("gnome-shell/theme.json"):
                        logging.info("New style theme detected (theme.json)")
                        #new style theme - extract the name from the json file
                        tmp = tempfile.mkdtemp()
                        z.extract(n, tmp)
                        with open(os.path.join(tmp,n)) as f:
                            try:
                                theme_name = json.load(f)["shell-theme"]["name"]
                            except:
                                logging.warning("Invalid theme format", exc_info=True)

                if not fragment:
                    raise Exception("Could not find gnome-shell.css")

                if not theme_name:
                    logging.info("Old style theme detected (theme.json)")
                    #old style themes name was taken from the zip name
                    if fragment[0] == "theme" and len(fragment) == 1:
                        theme_name = os.path.basename(f)
                    else:
                        theme_name = fragment[0]

                theme_members_path = "/".join(fragment)

                ok, updated = extract_zip_file(
                                z,
                                theme_members_path,
                                os.path.join(ShellThemeTweak.THEME_DIR, theme_name, "gnome-shell"))

                if ok:
                    if updated:
                        self.notify_info(_("%s theme updated successfully") % theme_name)
                    else:
                        self.notify_info(_("%s theme installed successfully") % theme_name)

                    #I suppose I could rely on updated as indicating whether to add the theme
                    #name to the combo, but just check to see if it is already there
                    model = self._combo.get_model()
                    if theme_name not in [r[0] for r in model]:
                        model.append( (theme_name, theme_name) )
                else:
                    self.notify_error(_("Error installing theme"))


            except:
                #does not look like a valid theme
                self.notify_error(_("Invalid theme"))
                logging.warning("Error parsing theme zip", exc_info=True)

        #set button back to default state
        chooser.unselect_all()

    def _on_combo_changed(self, combo):
        val = combo.get_model().get_value(combo.get_active_iter(), 0)
        self._settings.set_string(ShellThemeTweak.THEME_GSETTINGS_NAME, val)

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
                    _("The shell may need to be restarted to apply the theme"),
                    _("Restart"),
                    lambda: self._shell.restart())

sg = build_horizontal_sizegroup()

TWEAK_GROUPS = (
        TweakGroup(
            _("Shell"),
            GSettingsSwitchTweak("org.gnome.shell.clock", "show-date", schema_filename="org.gnome.shell.gschema.xml"),
            GSettingsSwitchTweak("org.gnome.shell.calendar", "show-weekdate", schema_filename="org.gnome.shell.gschema.xml"),
            ShowWindowButtons(size_group=sg),
            ShellThemeTweak(size_group=sg),
            GSettingsComboEnumTweak("org.gnome.settings-daemon.plugins.power", "lid-close-battery-action", size_group=sg),
            GSettingsComboEnumTweak("org.gnome.settings-daemon.plugins.power", "lid-close-ac-action", size_group=sg)),
)
