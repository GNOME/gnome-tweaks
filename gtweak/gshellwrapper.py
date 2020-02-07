# Copyright (c) 2011 John Stowers
# SPDX-License-Identifier: GPL-3.0+
# License-Filename: LICENSES/GPL-3.0

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

        self.proxy_extensions = Gio.DBusProxy.new_sync(
                            d, 0, None,
                            'org.gnome.Shell',
                            '/org/gnome/Shell',
                            'org.gnome.Shell.Extensions',
                            None)

        val = self.proxy.get_cached_property("Mode")
        if val is not None:
            self._mode = val.unpack()
        else:
            logging.warning("Error getting shell mode")
            self._mode = "user"

        val = self.proxy.get_cached_property("ShellVersion")
        if val is not None:
            self._version = val.unpack()
        else:
            logging.critical("Error getting shell version")
            self._version = "0.0.0"

    @property
    def mode(self):
        return self._mode

    @property
    def version(self):
        return self._version


class GnomeShell:

    EXTENSION_STATE = {
        "ENABLED"       :   1,
        "DISABLED"      :   2,
        "ERROR"         :   3,
        "OUT_OF_DATE"   :   4,
        "DOWNLOADING"   :   5,
        "INITIALIZED"   :   6,
    }

    EXTENSION_TYPE = {
        "SYSTEM"        :   1,
        "PER_USER"      :   2
    }

    DATA_DIR = os.path.join(GLib.get_user_data_dir(), "gnome-shell")
    EXTENSION_DIR = os.path.join(GLib.get_user_data_dir(), "gnome-shell", "extensions")
    EXTENSION_ENABLED_KEY = "enabled-extensions"
    SUPPORTS_EXTENSION_PREFS = True

    def __init__(self, shellproxy, shellsettings):
        self._proxy = shellproxy
        self._settings = shellsettings

    def _execute_js(self, js):
        result, output = self._proxy.proxy.Eval('(s)', js)
        if not result:
            raise Exception(output)
        return output

    def restart(self):
        self._execute_js('global.reexec_self();')

    def reload_theme(self):
        self._execute_js('const Main = imports.ui.main; Main.loadTheme();')

    def extension_is_active(self, state, uuid):
        return state == GnomeShell.EXTENSION_STATE["ENABLED"] and \
                self._settings.setting_is_in_list(self.EXTENSION_ENABLED_KEY, uuid)

    def enable_extension(self, uuid):
        self._settings.setting_add_to_list(self.EXTENSION_ENABLED_KEY, uuid)

    def disable_extension(self, uuid):
        self._settings.setting_remove_from_list(self.EXTENSION_ENABLED_KEY, uuid)

    def list_extensions(self):
        return self._proxy.proxy_extensions.ListExtensions()

    def uninstall_extension(self, uuid):
        return self._proxy.proxy_extensions.UninstallExtension('(s)', uuid)

    def install_remote_extension(self, uuid, reply_handler, error_handler, user_data):
        self._proxy.proxy_extensions.InstallRemoteExtension('(s)', uuid,
            result_handler=reply_handler, error_handler=error_handler, user_data=user_data)

    @property
    def mode(self):
        return self._proxy.mode

    @property
    def version(self):
        return self._proxy.version


@gtweak.utils.singleton
class GnomeShellFactory:
    def __init__(self):
        try:
            proxy = _ShellProxy()
            settings = GSettingsSetting("org.gnome.shell")
            v = list(map(int, proxy.version.split(".")))

            self.shell = GnomeShell(proxy, settings)

            logging.debug("Shell version: %s", str(v))
        except:
            self.shell = None
            logging.warn("Shell not installed or running")

    def get_shell(self):
        return self.shell


if __name__ == "__main__":
    gtweak.GSETTINGS_SCHEMA_DIR = "/usr/share/glib-2.0/schemas/"

    logging.basicConfig(format="%(levelname)-8s: %(message)s", level=logging.DEBUG)

    s = GnomeShellFactory().get_shell()
    print("Shell Version: %s" % s.version)
    print(s.list_extensions())

    print(s == GnomeShellFactory().get_shell())
