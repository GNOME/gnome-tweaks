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

import logging
import os.path
import xml.dom.minidom

import gtweak

from gi.repository import Gio, GLib

_SCHEMA_CACHE = {}
_GSETTINGS_SCHEMAS = set(Gio.Settings.list_schemas())

class GSettingsMissingError(Exception):
    pass

class _GSettingsSchema:
    def __init__(self, schema_name, schema_dir=None, schema_filename=None, **options):
        if not schema_dir:
            schema_dir = gtweak.GSETTINGS_SCHEMA_DIR
        if not schema_filename:
            schema_filename = schema_name + ".gschema.xml"

        schema_path = os.path.join(schema_dir, schema_filename)
        if not os.path.exists(schema_path):
            logging.critical("Could not find schema %s" % schema_path)
            assert(False)

        self._schema_name = schema_name
        self._schema = {}

        try:
            dom = xml.dom.minidom.parse(schema_path)
            for schema in dom.getElementsByTagName("schema"):
                if schema_name == schema.getAttribute("id"):
                    for key in schema.getElementsByTagName("key"):
                        #summary is compulsory, description is optional
                        #... in theory, but we should not barf on bad schemas ever
                        try:
                            summary = key.getElementsByTagName("summary")[0].childNodes[0].data
                        except:
                            summary = ""
                            logging.warning("Schema %s missing summary text: %s" % (schema_path, key.toxml()))
                        try:
                            description = key.getElementsByTagName("description")[0].childNodes[0].data
                        except:
                            description = ""
                        self._schema[key.getAttribute("name")] = {
                                "summary"       :   summary,
                                "description"   :   description
                        }
        except:
            logging.critical("Error parsing schema %s (%s)" % (schema_name, schema_path), exc_info=True)

    def __repr__(self):
        return "<gtweak.gsettings._GSettingsSchema: %s>" % self._schema_name

class GSettingsFakeSetting:
    def __init__(self):
        pass

    def get_range(self, *args, **kwargs):
        return False, []

    def get_string(self, *args, **kwargs):
        return ""

    def __getattr__(self, name):
        def noop(*args, **kwargs):
            pass
        return noop

class GSettingsSetting(Gio.Settings):
    def __init__(self, schema_name, **options):
        if schema_name not in _GSETTINGS_SCHEMAS:
            raise GSettingsMissingError(schema_name)
        Gio.Settings.__init__(self, schema_name)
        if schema_name not in _SCHEMA_CACHE:
            _SCHEMA_CACHE[schema_name] = _GSettingsSchema(schema_name, **options)
            logging.debug("Caching gsettings: %s" % _SCHEMA_CACHE[schema_name])

        self._schema = _SCHEMA_CACHE[schema_name]

        if gtweak.VERBOSE:
            self.connect("changed", self._on_changed)

    def _on_changed(self, settings, key_name):
        print "Change: %s %s -> %s" % (self.props.schema, key_name, self[key_name])

    def _setting_check_is_list(self, key):
        variant = Gio.Settings.get_value(self, key)
        return variant.get_type_string() == "as"

    def schema_get_summary(self, key):
        return self._schema._schema[key]["summary"]
        
    def schema_get_description(self, key):
        return self._schema._schema[key]["description"]

    def schema_get_all(self, key):
        return self._schema._schema[key]

    def setting_add_to_list(self, key, value):
        """ helper function, ensures value is present in the GSettingsList at key """
        assert self._setting_check_is_list(key)

        vals = self[key]
        if value not in vals:
            vals.append(value)
            self[key] = vals
            return True

    def setting_remove_from_list(self, key, value):
        """ helper function, removes value in the GSettingsList at key (if present)"""
        assert self._setting_check_is_list(key)

        vals = self[key]
        try:
            vals.remove(value)
            self[key] = vals
            return True
        except ValueError:
            #not present
            pass

    def setting_is_in_list(self, key, value):
        assert self._setting_check_is_list(key)
        return value in self[key]

if __name__ == "__main__":
    gtweak.GSETTINGS_SCHEMA_DIR = "/usr/share/glib-2.0/schemas/"

    key = "draw-background"
    s = GSettingsSetting("org.gnome.desktop.background")
    print s.schema_get_summary(key), s.schema_get_description(key)

    key = "disabled-extensions"
    s = GSettingsSetting("org.gnome.shell")
    assert s.setting_add_to_list(key, "foo")
    assert s.setting_remove_from_list(key, "foo")
    assert not s.setting_remove_from_list(key, "foo")
