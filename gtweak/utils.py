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

from gi.repository import GLib

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

class AutostartManager:
    def __init__(self, DATA_DIR, desktop_filename, exec_cmd="", extra_exec_args=""):
        self._desktop_filename = desktop_filename
        self._desktop_file = os.path.join(DATA_DIR, "applications", desktop_filename)
        self._exec_cmd = exec_cmd
        self._extra_exec_args = " %s\n" % extra_exec_args
        
        user_autostart_dir = os.path.join(GLib.get_user_config_dir(), "autostart")
        if not os.path.isdir(user_autostart_dir):
            try:
                os.makedirs(user_autostart_dir)
            except:
                logging.critical("Could not create autostart dir: %s" % user_autostart_dir)
        self._autostart_file = os.path.join(user_autostart_dir, desktop_filename)

    def is_start_at_login_enabled(self):
        if os.path.exists(self._autostart_file):
            #if it contains X-GNOME-Autostart-enabled=false then it has
            #has been disabled by the user in the session applet, otherwise
            #it is enabled
            return open(self._autostart_file).read().find("X-GNOME-Autostart-enabled=false") == -1
        else:
            return False

    def update_start_at_login(self, update):
        logging.debug("Updating autostart %s -> %s" % (self._desktop_filename, update))

        if os.path.exists(self._autostart_file):
            logging.info("Removing autostart %s" % self._autostart_file)
            os.remove(self._autostart_file)

        if update:
            if not os.path.exists(self._desktop_file):
                logging.critical("Could not find desktop file: %s" % self._desktop_file)
                return

            logging.info("Adding autostart %s" % self._autostart_file)
            #copy the original file to the new file, but add the extra exec args
            old = open(self._desktop_file, "r")
            new = open(self._autostart_file, "w")

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
