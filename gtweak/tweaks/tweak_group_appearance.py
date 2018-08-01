# Copyright (c) 2011 John Stowers
# SPDX-License-Identifier: GPL-3.0+
# License-Filename: LICENSES/GPL-3.0

import os
import os.path
import logging
import zipfile
import tempfile
import json
import pprint
import configparser

from gi.repository import Gtk
from gi.repository import GLib

import gtweak
from gtweak.utils import walk_directories, make_combo_list_with_default, extract_zip_file, get_resource_dirs
from gtweak.tweakmodel import Tweak
from gtweak.gshellwrapper import GnomeShellFactory
from gtweak.gsettings import GSettingsSetting
from gtweak.gtksettings import GtkSettingsManager
from gtweak.widgets import ListBoxTweakGroup, GSettingsSwitchTweak, GSettingsComboTweak, GSettingsComboEnumTweak, Title, build_combo_box_text,build_label_beside_widget, FileChooserButton, GSettingsFileChooserButtonTweak

_shell = GnomeShellFactory().get_shell()
_shell_loaded = _shell is not None

def get_theme_name(index_path):
    """Given an index file path, gets the relevant sound theme's name."""
    config = configparser.ConfigParser()
    config.read(index_path)
    return config["Sound Theme"]["Name"]

def get_sound_themes():
    """Gets the available sound themes as a (theme_directory_name, theme_display_name) tuple list."""
    themes = []
    seen = set()
    for location in get_resource_dirs("sounds"):
        for item in os.listdir(location):
            candidate = os.path.join(location, item)
            index_file = os.path.join(candidate, "index.theme")
            if os.path.isdir(candidate) and os.path.exists(index_file):
                theme_info = (os.path.basename(candidate), get_theme_name(index_file))
                if theme_info[1] not in seen:
                    themes.append(theme_info)
                    seen.add(theme_info[1])
    return themes



class GtkThemeSwitcher(GSettingsComboTweak):
    def __init__(self, **options):
        GSettingsComboTweak.__init__(self,
			_("Applications"),
            "org.gnome.desktop.interface",
            "gtk-theme",
            make_combo_list_with_default(self._get_valid_themes(), "Adwaita"),
            **options)

        self._gtksettings3 = GtkSettingsManager('3.0')
        self._gtksettings4 = GtkSettingsManager('4.0')

    def _get_valid_themes(self):
        """ Only shows themes that have variations for gtk3"""
        gtk_ver = Gtk.MINOR_VERSION
        if gtk_ver % 2: # Want even number
            gtk_ver += 1

        valid = ['Adwaita', 'HighContrast', 'HighContrastInverse']
        valid += walk_directories(get_resource_dirs("themes"), lambda d:
                    os.path.exists(os.path.join(d, "gtk-3.0", "gtk.css")) or \
                         os.path.exists(os.path.join(d, "gtk-3.{}".format(gtk_ver))))
        return set(valid)

    def _on_combo_changed(self, combo):
        _iter = combo.get_active_iter()
        if _iter:
            value = combo.get_model().get_value(_iter, 0)
            self.settings.set_string(self.key_name, value)
        # Turn off Global Dark Theme when theme is changed.
        # https://bugzilla.gnome.org/783666
        try:
            self._gtksettings3.set_integer("gtk-application-prefer-dark-theme",
                                          0)
            self._gtksettings4.set_integer("gtk-application-prefer-dark-theme",
                                          0)
        except:
            self.notify_information(_("Error writing setting"))


class IconThemeSwitcher(GSettingsComboTweak):
    def __init__(self, **options):
        GSettingsComboTweak.__init__(self,
			_("Icons"),
			"org.gnome.desktop.interface",
            "icon-theme",
            make_combo_list_with_default(self._get_valid_icon_themes(), "Adwaita"),
            **options)

    def _get_valid_icon_themes(self):
        valid = walk_directories(get_resource_dirs("icons"), lambda d:
                    os.path.isdir(d) and \
			os.path.exists(os.path.join(d, "index.theme")))
        return set(valid)

class CursorThemeSwitcher(GSettingsComboTweak):
    def __init__(self, **options):
        GSettingsComboTweak.__init__(self,
			_("Cursor"),
            "org.gnome.desktop.interface",
            "cursor-theme",
            make_combo_list_with_default(self._get_valid_cursor_themes(), "Adwaita"),
            **options)

    def _get_valid_cursor_themes(self):
        valid = walk_directories(get_resource_dirs("icons"), lambda d:
                    os.path.isdir(d) and \
                        os.path.exists(os.path.join(d, "cursors")))
        return set(valid)

class ShellThemeTweak(Gtk.Box, Tweak):

    THEME_EXT_NAME = "user-theme@gnome-shell-extensions.gcampax.github.com"
    THEME_GSETTINGS_SCHEMA = "org.gnome.shell.extensions.user-theme"
    THEME_GSETTINGS_NAME = "name"
    THEME_GSETTINGS_DIR = os.path.join(GLib.get_user_data_dir(), "gnome-shell", "extensions",
                                       THEME_EXT_NAME, "schemas")
    LEGACY_THEME_DIR = os.path.join(GLib.get_home_dir(), ".themes")
    THEME_DIR = os.path.join(GLib.get_user_data_dir(), "themes")

    def __init__(self, **options):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.HORIZONTAL)
        Tweak.__init__(self, _("Shell"), _("Install custom or user themes for gnome-shell"), **options)

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
                            "Could not find user-theme extension in %s" % ','.join(list(extensions.keys())),
                            exc_info=True)
                        error = _("Shell user-theme extension incorrectly installed")

                else:
                    error = _("Shell user-theme extension not enabled")
            except Exception as e:
                logging.warning("Could not list shell extensions", exc_info=True)
                error = _("Could not list shell extensions")

        if error:
            cb = build_combo_box_text(None)
            build_label_beside_widget(self.name, cb,
                        warning=error,
                        hbox=self)
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
            valid = set(valid)

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

            build_label_beside_widget(self.name, chooser, cb, hbox=self)
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
                        self.notify_information(_("%s theme updated successfully") % theme_name)
                    else:
                        self.notify_information(_("%s theme installed successfully") % theme_name)

                    #I suppose I could rely on updated as indicating whether to add the theme
                    #name to the combo, but just check to see if it is already there
                    model = self._combo.get_model()
                    if theme_name not in [r[0] for r in model]:
                        model.append( (theme_name, theme_name) )
                else:
                    self.notify_information(_("Error installing theme"))


            except:
                #does not look like a valid theme
                self.notify_information(_("Invalid theme"))
                logging.warning("Error parsing theme zip", exc_info=True)

        #set button back to default state
        chooser.unselect_all()

    def _on_combo_changed(self, combo):
        val = combo.get_model().get_value(combo.get_active_iter(), 0)
        self._settings.set_string(ShellThemeTweak.THEME_GSETTINGS_NAME, val)


TWEAK_GROUPS = [
    ListBoxTweakGroup(_("Appearance"),
        #GSettingsSwitchTweak("Buttons Icons","org.gnome.desktop.interface", "buttons-have-icons"),
        #GSettingsSwitchTweak("Menu Icons","org.gnome.desktop.interface", "menus-have-icons"),
        Title(_("Themes"), "", uid="title-theme"),
        GtkThemeSwitcher(),
        CursorThemeSwitcher(),
        IconThemeSwitcher(),
        ShellThemeTweak(loaded=_shell_loaded),
        GSettingsComboTweak(_("Sound"), "org.gnome.desktop.sound", "theme-name", get_sound_themes(),
                        desc=_("Specifies which sound theme to use for sound events.")),

        Title(_("Background"), "", uid="title-theme"),
        GSettingsFileChooserButtonTweak(_("Image"),"org.gnome.desktop.background", "picture-uri",
            local_only=True, mimetypes=["application/xml","image/png","image/jpeg"]),
        GSettingsComboEnumTweak(_("Adjustment"),"org.gnome.desktop.background", "picture-options"),

        Title(_("Lock Screen"), "", uid="title-theme"),
        GSettingsFileChooserButtonTweak(_("Image"),"org.gnome.desktop.screensaver", "picture-uri",
            local_only=True, mimetypes=["application/xml","image/png","image/jpeg"]),
        GSettingsComboEnumTweak(_("Adjustment"),"org.gnome.desktop.screensaver", "picture-options"),

        # Title(_("Files"), ""),
        # GSettingsSwitchTweak(_("Use location entry"), "org.gnome.nautilus.preferences",
        # "always-use-location-entry",schema_filename="org.gnome.nautilus.gschema.xml"),
    ),
]
