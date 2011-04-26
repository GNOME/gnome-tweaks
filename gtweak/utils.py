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

from gi.repository import GLib

class AutostartManager:
    def __init__(self, DATA_DIR, desktop_filename, extra_exec_args=""):
        self._desktop_file = os.path.join(DATA_DIR, desktop_filename)
        self._autostart_file = os.path.join(
                                    GLib.get_user_config_dir(), "autostart", desktop_filename)
        self._extra_exec_args = " %s\n" % extra_exec_args

    def is_start_at_login_enabled(self):
        if os.path.exists(self._autostart_file):
            #if it contains X-GNOME-Autostart-enabled=false then it has
            #has been disabled by the user in the session applet, otherwise
            #it is enabled
            return open(self._autostart_file).read().find("X-GNOME-Autostart-enabled=false") == -1
        else:
            return False

    def update_start_at_login(self, update):

        if os.path.exists(self._autostart_file):
            log.info("Removing autostart desktop file")
            os.remove(self._autostart_file)

        if update:
            if not os.path.exists(self._desktop_file):
                log.critical("Could not find desktop file: %s" % self._desktop_file)
                return

            log.info("Adding autostart desktop file")
            #copy the original file to the new file, but add the extra exec args
            old = open(self._desktop_file, "r")
            new = open(self._autostart_file, "w")

            for l in old.readlines():         
                if l.startswith("Exec="):
                    new.write(l[0:-1])
                    new.write(self._extra_exec_args)
                else:
                    new.write(l)

            old.close()
            new.close()
