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
import json
import logging

from gi.repository import Gio
from gi.repository import GLib

import gtweak.utils
from gtweak.gsettings import GSettingsSetting

class _ShellProxy:
    def __init__(self):
        d = Gio.bus_get_sync(Gio.BusType.SESSION, None)
        self.proxy = Gio.DBusProxy.new_sync(
                            d, 0, None,
                            'org.gnome.Shell',
                            '/org/gnome/Shell',
                            'org.gnome.Shell',
                            None)

    def execute_js(self, js):
        result, output = self.proxy.Eval('(s)', js)
        if not result:
            raise Exception(output)
        return output

    @property
    def version(self):
        return json.loads(self.execute_js('const Config = imports.misc.config; Config.PACKAGE_VERSION'))

class GnomeShell:

    EXTENSION_STATE = {
        "ENABLED"       :   1,
        "DISABLED"      :   2,
        "ERROR"         :   3,
        "OUT_OF_DATE"   :   4
    }

    EXTENSION_TYPE = {
        "SYSTEM"        :   1,
        "PER_USER"      :   2
    }

    DATA_DIR = os.path.join(GLib.get_user_data_dir(), "gnome-shell")

    def __init__(self, shellproxy, shellsettings):
        self._proxy = shellproxy
        self._settings = shellsettings

    def restart(self):
        self._proxy.execute_js('global.reexec_self();')

    def reload_theme(self):
        self._proxy.execute_js('const Main = imports.ui.main; Main.loadTheme();')

    @property
    def version(self):
        return self._proxy.version

class GnomeShell30(GnomeShell):

    EXTENSION_DISABLED_KEY = "disabled-extensions"
    EXTENSION_NEED_RESTART = True

    def __init__(self, *args, **kwargs):
        GnomeShell.__init__(self, *args, **kwargs)

    def list_extensions(self):
        out = self._proxy.execute_js('const ExtensionSystem = imports.ui.extensionSystem; ExtensionSystem.extensionMeta')
        return json.loads(out)

    def extension_is_active(self, state, uuid):
        return state == GnomeShell.EXTENSION_STATE["ENABLED"] and \
                not self._settings.setting_is_in_list(self.EXTENSION_DISABLED_KEY, uuid)

    def enable_extension(self, uuid):
        self._settings.setting_remove_from_list(self.EXTENSION_DISABLED_KEY, uuid)

    def disable_extension(self, uuid):
        self._settings.setting_add_to_list(self.EXTENSION_DISABLED_KEY, uuid)

class GnomeShell32(GnomeShell):

    EXTENSION_ENABLED_KEY = "enabled-extensions"
    EXTENSION_NEED_RESTART = False

    def list_extensions(self):
        return self._proxy.ListExtensions()

    def extension_is_active(self, state, uuid):
        return state == GnomeShell.EXTENSION_STATE["ENABLED"] and \
                self._settings.setting_is_in_list(self.EXTENSION_ENABLED_KEY, uuid)

    def enable_extension(self, uuid):
        self._settings.setting_add_to_list(self.EXTENSION_ENABLED_KEY, uuid)

    def disable_extension(self, uuid):
        self._settings.setting_remove_from_list(self.EXTENSION_ENABLED_KEY, uuid)

@gtweak.utils.singleton
class GnomeShellFactory:
    def __init__(self):
        proxy = _ShellProxy()
        settings = GSettingsSetting("org.gnome.shell")
        v = map(int,proxy.version.split("."))

        if v >= [3,1,4]:
            self.shell = GnomeShell32(proxy, settings)
        else:
            self.shell = GnomeShell30(proxy, settings)

        logging.debug("Shell version: %s", str(v))

    def get_shell(self):
        return self.shell

if __name__ == "__main__":
    gtweak.GSETTINGS_SCHEMA_DIR = "/usr/share/glib-2.0/schemas/"

    s = GnomeShellFactory().get_shell()
    print "Shell Version: %s" % s.version
    print s.list_extensions()

    print s == GnomeShellFactory().get_shell()
