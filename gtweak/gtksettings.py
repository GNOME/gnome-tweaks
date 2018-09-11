# Copyright (c) 2012 Cosimo Cecchi
# SPDX-License-Identifier: GPL-3.0+
# License-Filename: LICENSES/GPL-3.0

import os.path
import logging

from gi.repository import GLib

SETTINGS_GROUP_NAME = "Settings"

LOG = logging.getLogger(__name__)


class GtkSettingsManager:
    def __init__(self, version):
        self._path = os.path.join(GLib.get_user_config_dir(),
                                  "gtk-" + version,
                                  "settings.ini")
        os.makedirs(os.path.dirname(self._path), exist_ok=True)

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
            GLib.file_set_contents(self._path, data[0].encode())
        except:
            raise
