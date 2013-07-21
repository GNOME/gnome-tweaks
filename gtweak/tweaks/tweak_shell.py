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
import pprint

from gi.repository import Gtk, GLib, GObject, Gio

from gtweak.utils import walk_directories, extract_zip_file, make_combo_list_with_default
from gtweak.gsettings import GSettingsSetting, GSettingsMissingError, GSettingsFakeSetting
from gtweak.gshellwrapper import GnomeShellFactory
from gtweak.tweakmodel import Tweak, TweakGroup, TWEAK_GROUP_APPEARANCE, TWEAK_GROUP_TOPBAR, TWEAK_GROUP_WINDOWS, TWEAK_GROUP_WORKSPACES, TWEAK_GROUP_POWER, TWEAK_SORT_FIRST, TWEAK_SORT_LAST
from gtweak.widgets import FileChooserButton, GSettingsComboTweak, GSettingsComboEnumTweak, GSettingsSwitchTweak, adjust_schema_for_overrides, build_label_beside_widget, build_horizontal_sizegroup, build_combo_box_text, UI_BOX_SPACING, Title

_shell = GnomeShellFactory().get_shell()
_shell_loaded = _shell is not None

class ShowWindowButtons(GSettingsComboTweak):
    def __init__(self, **options):
        GSettingsComboTweak.__init__(self,
			"Title Bar Buttons",
            "org.gnome.desktop.wm.preferences",
            "button-layout",
            ((':close', _("Close Only")),
            (':minimize,close', _("Minimize and Close")),
            (':maximize,close', _("Maximize and Close")),
            (':minimize,maximize,close', _("All"))),
            loaded=_shell_loaded,
            **options)

class ShellThemeTweak(Tweak):

    THEME_EXT_NAME = "user-theme@gnome-shell-extensions.gcampax.github.com"
    THEME_GSETTINGS_SCHEMA = "org.gnome.shell.extensions.user-theme"
    THEME_GSETTINGS_NAME = "name"
    THEME_GSETTINGS_DIR = os.path.join(GLib.get_user_data_dir(), "gnome-shell", "extensions",
                                       THEME_EXT_NAME, "schemas")
    LEGACY_THEME_DIR = os.path.join(GLib.get_home_dir(), ".themes")
    THEME_DIR = os.path.join(GLib.get_user_data_dir(), "themes")

    def __init__(self, **options):
        Tweak.__init__(self, _("Shell theme"), _("Install custom or user themes for gnome-shell"), **options)

        #check the shell is running and the usertheme extension is present
        error = _("Unknown error")
        self._shell = _shell

        if self._shell is None:
            logging.warning("Shell not running", exc_info=True)
            error = _("Shell not running")
        else:
            try:
                extensions = self._shell.list_extensions()
                if ShellThemeTweak.THEME_EXT_NAME in extensions and extensions[ShellThemeTweak.THEME_EXT_NAME]["state"] == 1:
                    #check the correct gsettings key is present
                    try:
                        if os.path.exists(ShellThemeTweak.THEME_GSETTINGS_DIR):
                            self._settings = GSettingsSetting(ShellThemeTweak.THEME_GSETTINGS_SCHEMA,
                                                              schema_dir=ShellThemeTweak.THEME_GSETTINGS_DIR)
                        else:
                            self._settings = GSettingsSetting(ShellThemeTweak.THEME_GSETTINGS_SCHEMA)
                        name = self._settings.get_string(ShellThemeTweak.THEME_GSETTINGS_NAME)

                        ext = extensions[ShellThemeTweak.THEME_EXT_NAME]
                        logging.debug("Shell user-theme extension\n%s" % pprint.pformat(ext))

                        error = None
                    except:
                        logging.warning(
                            "Could not find user-theme extension in %s" % ','.join(extensions.keys()),
                            exc_info=True)
                        error = _("Shell user-theme extension incorrectly installed")

                else:
                    error = _("Shell user-theme extension not enabled")
            except Exception, e:
                logging.warning("Could not list shell extensions", exc_info=True)
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
            dirs += [ShellThemeTweak.LEGACY_THEME_DIR]

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
            chooser = FileChooserButton(
                        _("Select a theme"),
                        True,
                        ["application/zip"])
            chooser.connect("file-set", self._on_file_set)

            self.widget = build_label_beside_widget(self.name, chooser, cb)
            self.widget_for_size_group = cb

            self.widget_sort_hint = TWEAK_SORT_LAST
    
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
                    logging.info("Old style theme detected (missing theme.json)")
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

class StaticWorkspaceTweak(Tweak):

    NUM_WORKSPACES_SCHEMA = "org.gnome.desktop.wm.preferences"
    NUM_WORKSPACES_KEY = "num-workspaces"

    DYNAMIC_KEY = "dynamic-workspaces"
    DYNAMIC_SCHEMA = "org.gnome.mutter"

    def __init__(self, **options):
        schema = adjust_schema_for_overrides(self.DYNAMIC_SCHEMA, self.DYNAMIC_KEY, options)
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

        self.widget = build_label_beside_widget(self.name, hb)
        self.widget_for_size_group = hb

sg = build_horizontal_sizegroup()

TWEAKS = (
    ShellThemeTweak(group_name=TWEAK_GROUP_APPEARANCE, loaded=_shell_loaded),
	ShowWindowButtons(group_name=TWEAK_GROUP_WINDOWS, size_group=sg),
	StaticWorkspaceTweak(size_group=sg, loaded=_shell_loaded, group_name=TWEAK_GROUP_WORKSPACES),
    GSettingsComboEnumTweak("Power Button Action", "org.gnome.settings-daemon.plugins.power", "button-power", size_group=sg, group_name=TWEAK_GROUP_POWER, sort=TWEAK_SORT_FIRST),
	Title("When Laptop Lid is Closed", "", group_name=TWEAK_GROUP_POWER),
    GSettingsComboEnumTweak("On Battery Power","org.gnome.settings-daemon.plugins.power", "lid-close-battery-action", size_group=sg, group_name=TWEAK_GROUP_POWER),
   	GSettingsComboEnumTweak("When plugged in","org.gnome.settings-daemon.plugins.power", "lid-close-ac-action", size_group=sg, group_name=TWEAK_GROUP_POWER),
    
)

TWEAK_GROUPS = (
    TweakGroup(
        TWEAK_GROUP_TOPBAR,
        GSettingsSwitchTweak("Show date","org.gnome.desktop.interface", "clock-show-date", schema_filename="org.gnome.desktop.interface.gschema.xml"),
        GSettingsSwitchTweak("Show seconds", "org.gnome.desktop.interface", "clock-show-seconds", schema_filename="org.gnome.desktop.interface.gschema.xml"),
        GSettingsSwitchTweak("Show week numbers","org.gnome.shell.calendar", "show-weekdate", schema_filename="org.gnome.shell.gschema.xml", loaded=_shell_loaded),
        ),
)
