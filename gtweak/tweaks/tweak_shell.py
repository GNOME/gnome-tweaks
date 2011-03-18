import os.path
import shutil
import zipfile
import tempfile

from gi.repository import Gtk
from gi.repository import GLib

from gtweak.gsettings import GSettingsSetting
from gtweak.gshellwrapper import GnomeShell
from gtweak.tweakmodel import Tweak, TweakGroup
from gtweak.widgets import GConfComboTweak, GSettingsComboEnumTweak, build_label_beside_widget, build_horizontal_sizegroup

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

class ThemeInstaller(Tweak):

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
            if ThemeInstaller.THEME_EXT_NAME in extensions and extensions[ThemeInstaller.THEME_EXT_NAME]["state"] == 1:
                #check the correct gsettings key is present
                try:
                    self._settings = GSettingsSetting(ThemeInstaller.THEME_GSETTINGS_SCHEMA)
                    name = self._settings.get_value(ThemeInstaller.THEME_GSETTINGS_NAME)
                    print "!!!!", name
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
            b = Gtk.Button.new_from_stock(Gtk.STOCK_REVERT_TO_SAVED)
            b.connect("clicked", self._on_revert)
            hb.pack_start(b, False, False, 5)

            chooser = _ThemeZipChooser()
            chooser.connect("file-set", self._on_file_set)
            hb.pack_start(chooser, False, False, 0)

            self.widget = build_label_beside_widget(self.name, hb)
            self.widget_for_size_group = chooser
    
    def _extract_theme_zip(self, z, theme_name):
        tmp = tempfile.mkdtemp()
        dest = os.path.join(ThemeInstaller.THEME_DIR, theme_name, "gnome-shell")
        try:
            if os.path.exists(dest):
                shutil.rmtree(dest)
            z.extractall(tmp)
            shutil.copytree(os.path.join(tmp, "theme"), dest)
            self._settings.set_value(ThemeInstaller.THEME_GSETTINGS_NAME, theme_name)
        except OSError:
            self.notify_error("Error installing theme")

    def _shell_reload_theme(self):
        #reloading the theme works OK, however there are some problems with reloading images.
        #https://bugzilla.gnome.org/show_bug.cgi?id=644125
        #however, smashing the whole shell just to change themes is pretty extreme. So we
        #just let the user-theme extension pick up the change by itself
        #
        #self._shell.reload_theme()
        #self.notify_action_required(
        #        "The shell must be restarted to apply the theme",
        #        "Restart",
        #        lambda: self._shell.restart())
        pass

    def _on_file_set(self, chooser):
        f = chooser.get_filename()

        with zipfile.ZipFile(f, 'r') as z:
            try:
                #check this looks like a valid theme
                info = z.getinfo('theme/gnome-shell.css')
                #the theme name is the filename, for the moment
                self._extract_theme_zip(
                        z,
                        os.path.splitext(os.path.basename(f))[0])
                self._shell_reload_theme()
            except KeyError:
                #does not look like a valid theme
                self.notify_error("Invalid theme file")
        #set button back to default state
        chooser.unselect_all()

    def _on_revert(self, btn):
        self._settings.set_value(ThemeInstaller.THEME_GSETTINGS_NAME, "")
        self._shell_reload_theme()



sg = build_horizontal_sizegroup()

TWEAK_GROUPS = (
        TweakGroup(
            "Shell",
            ShowWindowButtons(size_group=sg),
            ThemeInstaller(size_group=sg),
            GSettingsComboEnumTweak("org.gnome.settings-daemon.plugins.power", "lid-close-battery-action", size_group=sg)),
)
