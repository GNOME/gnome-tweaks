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

import gtweak
from gtweak.gsettings import GSettingsSetting
from gtweak.gconf import GConfSetting

from gi.repository import GLib

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

class AutostartManager:
    def __init__(self, desktop_filename, autostart_desktop_filename="", exec_cmd="", extra_exec_args=""):
        self.desktop_filename = desktop_filename
        self._autostart_desktop_filename = autostart_desktop_filename or desktop_filename
        self._exec_cmd = exec_cmd
        self._extra_exec_args = " %s\n" % extra_exec_args

        user_autostart_dir = os.path.join(GLib.get_user_config_dir(), "autostart")
        if not os.path.isdir(user_autostart_dir):
            try:
                os.makedirs(user_autostart_dir)
            except:
                logging.critical("Could not create autostart dir: %s" % user_autostart_dir)

        #find the desktop file
        self._desktop_file = ""
        for f in self._get_desktop_files():
            if os.path.exists(f):
                self._desktop_file = f
        self._user_autostart_file = os.path.join(user_autostart_dir, self._autostart_desktop_filename)

        logging.debug("Found desktop file: %s" % self._desktop_file)
        logging.debug("User autostart desktop file: %s" % self._user_autostart_file)

    def _get_system_autostart_files(self):
        return [
            os.path.join(d, "autostart", self._autostart_desktop_filename)
                for d in GLib.get_system_config_dirs()]

    def _get_desktop_files(self):
        dirs = [gtweak.DATA_DIR, GLib.get_user_data_dir()]
        dirs.extend(GLib.get_system_data_dirs())
        return [os.path.join(d, "applications", self.desktop_filename) for d in dirs]

    def get_autostart_condition(self):
        for f in self._get_system_autostart_files():
            if os.path.exists(f):
                with open(f, 'r') as f:
                    for l in f.readlines():
                        if l.startswith("AutostartCondition="):
                            return l.split("=")[-1].strip()
        return None

    def uses_autostart_condition(self, autostart_type=None):
        asc = self.get_autostart_condition()
        try:
            if autostart_type:
                return asc.split(" ", 1)[0] == autostart_type
            else:
                return asc != None
        except:
            logging.warning("Testing for expected AutostartCondition failed: Got (%s)" % asc, exc_info=True)
            return False

    def is_start_at_login_enabled(self):
        if os.path.exists(self._user_autostart_file):
            #prefer user directories first
            #if it contains X-GNOME-Autostart-enabled=false then it has
            #has been disabled by the user in the session applet, otherwise
            #it is enabled
            return open(self._user_autostart_file).read().find("X-GNOME-Autostart-enabled=false") == -1
        else:
            #check the system directories
            for f in self._get_system_autostart_files():
                if os.path.exists(f):
                    return True
        return False

    def update_start_at_login(self, update):

        if os.path.exists(self._user_autostart_file):
            logging.info("Removing user autostart file %s" % self._user_autostart_file)
            os.remove(self._user_autostart_file)

        asc = self.get_autostart_condition()
        if asc:
            #AutostartCondition=GNOME /desktop/gnome/interface/accessibility
            #AutostartCondition=GNOME3 if-session gnome-fallback
            #AutostartCondition=GSettings org.gnome.desktop.background show-desktop-icons
            method, value = asc.split(" ", 1)
            try:
                logging.info("Changing AutostartCondition %s -> %s" % (method, update))
                if method == "GSettings":
                    schema, key = value.split(" ")
                    GSettingsSetting(schema).set_boolean(key, update)
                elif method == "GNOME":
                    GConfSetting(shema, bool).set_value(update)
                else:
                    raise Exception("Method not supported")
            except:
                logging.warning("Autostart desktop file unsupported AutostartCondition (%s)" % asc, exc_info=True)

            return

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

if __name__ == "__main__":
    gtweak.DATA_DIR = "/usr/share"
    gtweak.GSETTINGS_SCHEMA_DIR = "/usr/share/glib-2.0/schemas/"

    logging.basicConfig(format="%(levelname)-8s: %(message)s", level=logging.DEBUG)

    d = AutostartManager("matlab.desktop")
    print d.desktop_filename, "uses autostartcondition", d.uses_autostart_condition()
    print d.desktop_filename, "autostarts", d.is_start_at_login_enabled()
    d.update_start_at_login(True)
    print d.desktop_filename, "autostarts", d.is_start_at_login_enabled()
    d.update_start_at_login(False)
    print d.desktop_filename, "autostarts", d.is_start_at_login_enabled()

    d = AutostartManager("orca.desktop", "orca-autostart.desktop")
    print d.desktop_filename, "uses autostartcondition", d.uses_autostart_condition()
    print d.desktop_filename, "autostartcondition is:", d.get_autostart_condition()
    print d.desktop_filename, "uses GSettings autostartcondition", d.uses_autostart_condition("GSettings")
    print d.desktop_filename, "autostarts", d.is_start_at_login_enabled()

    d = AutostartManager("dropbox.desktop")
    print d.desktop_filename, "uses autostartcondition", d.uses_autostart_condition()
    print d.desktop_filename, "autostarts", d.is_start_at_login_enabled()

    d = AutostartManager("nautilus.desktop", "nautilus-autostart.desktop")
    print d.desktop_filename, "uses autostartcondition", d.uses_autostart_condition()
    d.update_start_at_login(False)
