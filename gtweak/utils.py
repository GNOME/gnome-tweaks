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
import logging
import tempfile
import shutil
import subprocess
import glob

import gtweak
from gtweak.gsettings import GSettingsSetting

from gi.repository import GObject
from gi.repository import GLib
from gi.repository import Gio
from gi.repository import Notify

def singleton(cls):
    """
    Singleton decorator that works with GObject derived types. The 'recommended'
    python one - http://wiki.python.org/moin/PythonDecoratorLibrary#Singleton
    does not (interacts badly with GObjectMeta
    """
    instances = {}
    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return getinstance

def make_combo_list_with_default(opts, default, title=True, default_text=None):
    """
    Turns a list of values into a list of value,name (where name is the
    display name a user will see in a combo box). If a value is opt is
    equal to that supplied in default the display name for that value is
    modified to "value <i>(default)</i>"

    @opts: a list of value
    @returns: a list of 2-tuples (value, name)
    """
    themes = []
    for t in opts:
        if t.lower() == "default" and t != default:
            #some themes etc are actually called default. Ick. Dont show them if they
            #are not the actual default value
            continue

        if title and len(t):
            name = t[0].upper() + t[1:]
        else:
            name = t

        if t == default:
            #indicates the default theme, e.g Adwaita (default)
            name = default_text or _("%s <i>(default)</i>") % name

        themes.append((t, name))
    return themes

def walk_directories(dirs, filter_func):
    valid = []
    try:
        for thdir in dirs:
            if os.path.isdir(thdir):
                for t in os.listdir(thdir):
                    if filter_func(os.path.join(thdir, t)):
                         valid.append(t)
    except:
        logging.critical("Error parsing directories", exc_info=True)
    return valid

def extract_zip_file(z, members_path, dest):
    """ returns (true_if_extracted_ok, true_if_updated) """
    tmp = tempfile.mkdtemp()
    tmpdest = os.path.join(tmp, members_path)

    ok = True
    updated = False
    try:
        if os.path.exists(dest):
            shutil.rmtree(dest)
            updated = True
        z.extractall(tmp)
        shutil.copytree(tmpdest, dest)
    except OSError:
        ok = False
        logging.warning("Error extracting zip", exc_info=True)

    if ok:
        logging.info("Extracted zip to %s, copied to %s" % (tmpdest, dest))

    return ok, updated

def execute_subprocess(cmd_then_args, block=True):
    p = subprocess.Popen(
            cmd_then_args,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, close_fds=True)
    if block:
        stdout, stderr = p.communicate()
        return stdout, stderr, p.returncode

@singleton
class AutostartManager:

    @staticmethod
    def get_desktop_files():
        return [a.get_filename() for a in Gio.app_info_get_all()]

    @staticmethod
    def get_user_autostart_files():
        return glob.glob(
                    os.path.join(
                        GLib.get_user_config_dir(), "autostart", "*.desktop")) 

    @staticmethod
    def get_system_autostart_files():
        f = []
        for d in GLib.get_system_config_dirs():
            f.extend( glob.glob(os.path.join(d, "autostart", "*.desktop")) )
        return f

class AutostartFile:
    def __init__(self, appinfo, autostart_desktop_filename="", exec_cmd="", extra_exec_args=""):
        self._desktop_file = appinfo.get_filename()
        self._autostart_desktop_filename = autostart_desktop_filename or os.path.basename(self._desktop_file)
        self._exec_cmd = exec_cmd
        self._extra_exec_args = " %s\n" % extra_exec_args

        user_autostart_dir = os.path.join(GLib.get_user_config_dir(), "autostart")
        if not os.path.isdir(user_autostart_dir):
            try:
                os.makedirs(user_autostart_dir)
            except:
                logging.critical("Could not create autostart dir: %s" % user_autostart_dir)

        self._user_autostart_file = os.path.join(user_autostart_dir, self._autostart_desktop_filename)

        logging.debug("Found desktop file: %s" % self._desktop_file)
        logging.debug("User autostart desktop file: %s" % self._user_autostart_file)

    def is_start_at_login_enabled(self):
        if os.path.exists(self._user_autostart_file):
            #prefer user directories first
            #if it contains X-GNOME-Autostart-enabled=false then it has
            #has been disabled by the user in the session applet, otherwise
            #it is enabled
            return open(self._user_autostart_file).read().find("X-GNOME-Autostart-enabled=false") == -1
        else:
            #check the system directories
            for f in AutostartManager().get_system_autostart_files():
                if os.path.basename(f) == self._autostart_desktop_filename:
                    return True
        return False

    def update_start_at_login(self, update):

        if os.path.exists(self._user_autostart_file):
            logging.info("Removing user autostart file %s" % self._user_autostart_file)
            os.remove(self._user_autostart_file)

        if update:
            if (not self._desktop_file) or (not os.path.exists(self._desktop_file)):
                logging.critical("Could not find desktop file: %s" % self._desktop_file)
                return

            logging.info("Adding autostart %s" % self._user_autostart_file)
            #copy the original file to the new file, but add the extra exec args
            old = open(self._desktop_file, "r")
            new = open(self._user_autostart_file, "w")

            for l in old.readlines():         
                if l.startswith("Exec="):
                    if self._exec_cmd:
                        new.write("Exec=%s\n" % self._exec_cmd)
                    else:
                        new.write(l[0:-1])
                        new.write(self._extra_exec_args)
                else:
                    new.write(l)

            old.close()
            new.close()

class SchemaList:

    __list = None

    def __init__(self):

        if SchemaList.__list == None:
            SchemaList.__list = []
            
    def get(self):
        return SchemaList.__list
    
    def insert(self, key_name, schema_name):
        v = [key_name, schema_name]
        SchemaList.__list.append(v)
    
    def reset(self):
        for i in SchemaList.__list:
            s = Gio.Settings(i[1])
            s.reset(i[0])
@singleton
class DisableExtension(GObject.GObject):
    
    __gsignals__ = {
        "disable-extension": (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE,()),
    }    
    
    def __init__(self):
        GObject.GObject.__init__(self)
    
    def disable(self):
        self.emit("disable-extension")

@singleton
class XSettingsOverrides:

    VARIANT_TYPES = {
        'Gtk/ShellShowsAppMenu': GLib.Variant.new_int32,
        'Gtk/EnablePrimaryPaste': GLib.Variant.new_int32,
    }

    def __init__(self):
        self._settings = Gio.Settings('org.gnome.settings-daemon.plugins.xsettings')
        self._variant = self._settings.get_value("overrides")

    def _dup_variant_as_dict(self):
        items = {}
        for k in self._variant.keys():
            try:
                #variant override doesnt support .items()
                v = self._variant[k]
                items[k] = self.VARIANT_TYPES[k](v)
            except KeyError:
                pass
        return items

    def _dup_variant(self):
        return GLib.Variant('a{sv}', self._dup_variant_as_dict())

    def _set_override(self, name, v):
        items = self._dup_variant_as_dict()
        items[name] = self.VARIANT_TYPES[name](v)
        n = GLib.Variant('a{sv}', items)
        self._settings.set_value('overrides', n)

    def _get_override(self, name, default):
        try:
            return self._variant[name]
        except KeyError:
            return default

    #while I could store meta type information in the VARIANT_TYPES
    #dict, its easiest to do default value handling and missing value
    #checks in dedicated functions
    def set_shell_shows_app_menu(self, v):
        self._set_override('Gtk/ShellShowsAppMenu', int(v))
    def get_shell_shows_app_menu(self):
        return self._get_override('Gtk/ShellShowsAppMenu', True)
    def set_enable_primary_paste(self, v):
        self._set_override('Gtk/EnablePrimaryPaste', int(v))
    def get_enable_primary_paste(self):
        return self._get_override('Gtk/EnablePrimaryPaste', True)

class Notification:
    def __init__(self, summary, body):
        if Notify.is_initted() or Notify.init("GNOME Tweak Tool"):
            self.notification = Notify.Notification.new(
                                    summary,
                                    body,
                                    'gnome-tweak-tool'
            )
            self.notification.set_hint(
                                "desktop-entry",
                                GLib.Variant('s', 'gnome-tweak-tool'))
            self.notification.show()
        else:
            raise Exception("Not Supported")

@singleton
class LogoutNotification:
    def __init__(self):
        if Notify.is_initted() or Notify.init("GNOME Tweak Tool"):
            self.notification = Notify.Notification.new(
                                "Configuration changes requiere restart",
                                "Your session needs to be restarted for settings to take effect",
                                'gnome-tweak-tool')
            self.notification.add_action(
                                "restart",
                                "Restart Session",
                                self._logout, None, None)
            self.notification.set_hint(
                                "desktop-entry",
                                GLib.Variant('s', 'gnome-tweak-tool'))
            self.notification.show()
        else:
            raise Exception("Not Supported")

    def _logout(self, btn, action, unknown):
        d = Gio.bus_get_sync(Gio.BusType.SESSION, None)
        proxy = Gio.DBusProxy.new_sync(
                       d,Gio.DBusProxyFlags.NONE, None,
                       'org.gnome.SessionManager', 
                       '/org/gnome/SessionManager', 
                       'org.gnome.SessionManager',
                       None)
        proxy.Logout('(u)', 0)

