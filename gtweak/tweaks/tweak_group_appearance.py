# Copyright (c) 2011 John Stowers
# SPDX-License-Identifier: GPL-3.0+
# License-Filename: LICENSES/GPL-3.0

import os
import os.path
import logging
import zipfile
import tempfile
import json

from gi.repository import Gtk
from gi.repository import GLib
from gtweak.tweakmodel import Tweak

from gtweak.utils import walk_directories, make_combo_list_with_default, extract_zip_file, get_resource_dirs
from gtweak.gshellwrapper import GnomeShellFactory
from gtweak.gtksettings import GtkSettingsManager
from gtweak.widgets import (TweakPreferencesPage, GSettingsTweakComboRow,TweakPreferencesGroup, GSettingsFileChooserButtonTweak, FileChooserButton, build_label_beside_widget)


_shell = GnomeShellFactory().get_shell()
_shell_loaded = _shell is not None

class GtkThemeSwitcher(GSettingsTweakComboRow):
    def __init__(self, **options):
        self._gtksettings3 = GtkSettingsManager('3.0')
        self._gtksettings4 = GtkSettingsManager('4.0')

        GSettingsTweakComboRow.__init__(self,
			_("Legacy Applications"),
            "org.gnome.desktop.interface",
            "gtk-theme",
            make_combo_list_with_default(self._get_valid_themes(), "Adwaita"),
            **options)


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

    def _on_combo_changed(self, combo, _):
        item = combo.get_selected_item()
        if item:
            value = item.value
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


class IconThemeSwitcher(GSettingsTweakComboRow):
    def __init__(self, **options):
        GSettingsTweakComboRow.__init__(self,
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

class CursorThemeSwitcher(GSettingsTweakComboRow):
    def __init__(self, **options):
        GSettingsTweakComboRow.__init__(self,
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

class ShellThemeTweak(GSettingsTweakComboRow):
    THEME_EXT_NAME = "user-theme@gnome-shell-extensions.gcampax.github.com"
    THEME_GSETTINGS_SCHEMA = "org.gnome.shell.extensions.user-theme"
    THEME_GSETTINGS_NAME = "name"
    THEME_GSETTINGS_DIR = os.path.join(GLib.get_user_data_dir(), "gnome-shell", "extensions",
                                       THEME_EXT_NAME, "schemas")
    LEGACY_THEME_DIR = os.path.join(GLib.get_home_dir(), ".themes")
    THEME_DIR = os.path.join(GLib.get_user_data_dir(), "themes")

    def __init__(self):
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
                    error = None

                else:
                    error = _("Shell user-theme extension not enabled")
            except Exception as e:
                logging.warning("Could not list shell extensions", exc_info=True)
                error = _("Could not list shell extensions")

        if error:
            valid = []
        else:
            #include both system, and user themes
            #note: the default theme lives in /system/data/dir/gnome-shell/theme
            #      and not themes/, so add it manually later
            dirs = [os.path.join(d, "themes") for d in GLib.get_system_data_dirs()]
            dirs += [ShellThemeTweak.THEME_DIR]
            dirs += [ShellThemeTweak.LEGACY_THEME_DIR]
            # add default theme directory since some alternative themes are installed here
            dirs += [os.path.join(d, "gnome-shell", "theme") for d in GLib.get_system_data_dirs()]

            valid = walk_directories(dirs, lambda d:
                    os.path.exists(os.path.join(d, "gnome-shell.css")) or \
                    (
                        os.path.exists(os.path.join(d, "gnome-shell")) and \
                        os.path.exists(os.path.join(d, "gnome-shell", "gnome-shell.css"))
                    ))
            #the default value to reset the shell is an empty string
            valid.extend( ("",) )
            valid = set(valid)
        
        # load the schema from the user installation of User Themes if it exists
        schema_dir = ShellThemeTweak.THEME_GSETTINGS_DIR if os.path.exists(ShellThemeTweak.THEME_GSETTINGS_DIR) else None

        # build a combo box with all the valid theme options
        GSettingsTweakComboRow.__init__(self,
		  title=_("Shell"),
          subtitle=error if error else None,
          schema_name=ShellThemeTweak.THEME_GSETTINGS_SCHEMA,
          schema_dir=schema_dir,
          key_name=ShellThemeTweak.THEME_GSETTINGS_NAME,
          key_options=make_combo_list_with_default(opts=list(valid), default="", default_text=_("Adwaita (default)")),
          loaded=_shell_loaded,
        )

class ShellThemeInstallerTweak(Gtk.Box, Tweak):
    def __init__(self, title, description=None, **options):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.HORIZONTAL)
        Tweak.__init__(self, title=title, description=description, **options)

        chooser = FileChooserButton(
                    _("Select a theme"),
                    ["application/zip"])
        chooser.connect("notify::file-uri", self._on_file_set)

        build_label_beside_widget(title, chooser, hbox=self)

        self.widget_for_size_group = None

    def _on_file_set(self, chooser: FileChooserButton, _pspec):
        f = chooser.get_absolute_path()

        if not f:
            return

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
                else:
                    self.notify_information(_("Error installing theme"))


            except:
                # does not look like a valid theme
                self.notify_information(_("Invalid theme"))
                logging.warning("Error parsing theme zip", exc_info=True)

        # set button back to default state
        chooser.props.file_uri = None


TWEAK_GROUP = TweakPreferencesPage("appearance", _("Appearance"),
  TweakPreferencesGroup( _("Styles"), "title-styles",
    CursorThemeSwitcher(),
    IconThemeSwitcher(),
    ShellThemeTweak(),
    GtkThemeSwitcher(),
  ),
  # TODO: The current installer is brittle and the interaction doesn't make sense
  # (you select a file and then it is un-selected with notifications informing
  # you if it installed correctly)
  #
  #   ShellThemeInstallerTweak(
  #     title=_("Install custom shell theme"),
  #     description=_("Install custom or user themes for GNOME shell"),
  #   ),
  TweakPreferencesGroup(
    _("Background"), "title-backgrounds",
    GSettingsFileChooserButtonTweak(
      _("Default Image"),
      "org.gnome.desktop.background",
      "picture-uri",
      mimetypes=["application/xml", "image/png", "image/jpeg"],
    ),
    GSettingsFileChooserButtonTweak(
      _("Dark Style Image"),
      "org.gnome.desktop.background",
      "picture-uri-dark",
      mimetypes=["application/xml", "image/png", "image/jpeg"],
    ),
    GSettingsTweakComboRow(
      _("Adjustment"), "org.gnome.desktop.background", "picture-options"
    ),
   ),
)
