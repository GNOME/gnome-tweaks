# This file is part of gnome-tweak-tool.
#
# Copyright (c) 2012 Cosimo Cecchi
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

import gtweak.utils

SETTINGS_GROUP_NAME = "Settings"

LOG = logging.getLogger(__name__)

class GtkSettingsManager:
    def __init__(self, version):
        self._path = os.path.join(GLib.get_user_config_dir(),
                                  "gtk-" + version,
                                  "settings.ini")
    def _get_keyfile(self):
        keyfile = None
        try:
            keyfile = GLib.KeyFile()
            keyfile.load_from_file(self._path, 0)
        except MemoryError:
            LOG.critical("You have an old PyGObject, no support fo KeyFiles", exc_info=True)
        finally:
            return keyfile

    def get_integer(self, key):
        keyfile = self._get_keyfile()
        try:
            result = keyfile.get_integer(SETTINGS_GROUP_NAME, key)
        except:
            result = 0

        return result

    def set_integer(self, key, value):
        keyfile = self._get_keyfile()
        keyfile.set_integer(SETTINGS_GROUP_NAME, key, value)

        try:
            data = keyfile.to_data()
            GLib.file_set_contents(self._path, data[0])
        except:
            raise
