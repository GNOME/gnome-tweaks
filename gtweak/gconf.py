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

import subprocess

from gi.repository import GConf

class GConfSetting:
    def __init__(self, key, _type):
        self._key = key
        self._type = _type

        assert(self._type in (str, bool))

        self._client = GConf.Client.get_default()
        self._cmd_cache = {}

    def _run_gconftool(self, command):
        if command not in self._cmd_cache:
            p = subprocess.Popen(
                    ["gconftool-2", command, self._key],
                    stdin=subprocess.PIPE, stdout=subprocess.PIPE, close_fds=True)
            stdout, stderr = p.communicate()
            if p.returncode == 0:
                self._cmd_cache[command] = stdout.strip()
            else:
                self._cmd_cache[command] = "ERROR: %s" % stderr.strip()

        print "Caching gconf: %s (%s)" % (self, command)
        return self._cmd_cache[command]

    def schema_get_summary(self):
        return self._run_gconftool("--short-docs") or self._key.split("/")[-1].replace("_"," ").title()
        
    def schema_get_description(self):
        return self._run_gconftool("--long-docs")

    def schema_get_all(self):
        return {"summary":self.schema_get_summary(), "description":self.schema_get_description()}

    def get_value(self):
        if self._type == bool:
            return self._client.get_bool(self._key)
        elif self._type == str:
            return self._client.get_string(self._key)
        else:
            assert(False)

    def set_value(self, value):
        if self._type == bool:
            self._client.set_bool(self._key, value)
        elif self._type == str:
            self._client.set_string(self._key, value)
        else:
            assert(False)

    def __repr__(self):
        return "<gtweak.gconf.GConfSetting: %s>" % self._key

if __name__ == "__main__":
    key = "/apps/metacity/general/compositing_manager"
    s = GConfSetting(key, bool)
    print s.schema_get_summary(), s.schema_get_description()
    print s.get_value()
