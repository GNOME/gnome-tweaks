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

    def list_extensions(self):
        return self._proxy.proxy_extensions.ListExtensions()

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

            self.shell = GnomeShell(proxy, settings)

            logging.debug("Shell version: %s", str(proxy.version))
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
