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

from gi.repository import Gio
from gi.repository import GLib

class _ShellProxy:
    def __init__(self):
        d = Gio.bus_get_sync(Gio.BusType.SESSION, None)
        self._proxy = Gio.DBusProxy.new_sync(
                            d, 0, None,
                            'org.gnome.Shell',
                            '/org/gnome/Shell',
                            'org.gnome.Shell',
                            None)

    def execute_js(self, js):
        result, output = self._proxy.Eval('(s)', js)
        if not result:
            raise Exception(output)
        return output

class GnomeShell:

    DATA_DIR = os.path.join(GLib.get_user_data_dir(), "gnome-shell")

    def __init__(self):
        self._proxy = _ShellProxy()

    def restart(self):
        self._proxy.execute_js('global.reexec_self();')

    def reload_theme(self):
        self._proxy.execute_js('const Main = imports.ui.main; Main.loadTheme();')

    def list_extensions(self):
        out = self._proxy.execute_js('const ExtensionSystem = imports.ui.extensionSystem; ExtensionSystem.extensionMeta')
        return json.loads(out)

if __name__ == "__main__":
    s = GnomeShell()
    print s.list_extensions()
