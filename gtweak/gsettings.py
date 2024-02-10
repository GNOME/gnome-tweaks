# Copyright (c) 2011 John Stowers
# SPDX-License-Identifier: GPL-3.0+
# License-Filename: LICENSES/GPL-3.0

import logging
import os.path
import xml.dom.minidom
import gettext

import gtweak

from gi.repository import Gio, GLib

_SCHEMA_CACHE = {}
_GSETTINGS_SCHEMAS = set(Gio.Settings.list_schemas())
_GSETTINGS_RELOCATABLE_SCHEMAS = set(Gio.Settings.list_relocatable_schemas())


class GSettingsMissingError(Exception):
    pass


class _GSettingsSchema:
    def __init__(self, schema_name, child_name=None, schema_dir=None, schema_filename=None, **options):
        if not schema_filename:
            schema_filename = schema_name + ".gschema.xml"
        if not schema_dir:
            schema_dir = gtweak.GSETTINGS_SCHEMA_DIR
            for xdg_dir in GLib.get_system_data_dirs():
                dir = os.path.join(xdg_dir, "glib-2.0", "schemas")
                if os.path.exists(os.path.join(dir, schema_filename)):
                    schema_dir = dir
                    break

        schema_path = os.path.join(schema_dir, schema_filename)
        if not os.path.exists(schema_path):
            logging.critical("Could not find schema %s" % schema_path)
            assert(False)

        self._schema_name = f"{schema_name}.{child_name}" if child_name else schema_name
        self._schema = {}

        try:
            dom = xml.dom.minidom.parse(schema_path)
            global_gettext_domain = dom.documentElement.getAttribute('gettext-domain')
            try:
                if global_gettext_domain:
                    # We can't know where the schema owner was installed, let's assume it's
                    # the same prefix as ours
                    global_translation = gettext.translation(global_gettext_domain, gtweak.LOCALE_DIR)
                else:
                    global_translation = gettext.NullTranslations()
            except IOError:
                global_translation = None
                logging.debug("No translated schema for %s (domain: %s)" % (self._schema_name, global_gettext_domain))
            for schema in dom.getElementsByTagName("schema"):
                gettext_domain = schema.getAttribute('gettext-domain')
                try:
                    if gettext_domain:
                        translation = gettext.translation(gettext_domain, gtweak.LOCALE_DIR)
                    else:
                        translation = global_translation
                except IOError:
                    translation = None
                    logging.debug("Schema not translated %s (domain: %s)" % (self._schema_name, gettext_domain))
                if self._schema_name == schema.getAttribute("id"):
                    for key in schema.getElementsByTagName("key"):
                        name = key.getAttribute("name")
                        # summary is 'compulsory', description is optional
                        # …in theory, but we should not barf on bad schemas ever
                        try:
                            summary = key.getElementsByTagName("summary")[0].childNodes[0].data
                        except:
                            summary = ""
                            logging.info("Schema missing summary %s (key %s)" %
                                         (os.path.basename(schema_path), name))
                        try:
                            description = key.getElementsByTagName("description")[0].childNodes[0].data
                        except:
                            description = ""

                        # if missing translations, use the untranslated values
                        self._schema[name] = dict(
                            summary=translation.gettext(summary) if translation else summary,
                            description=translation.gettext(description) if translation else description
                        )

        except:
            logging.critical("Error parsing schema %s (%s)" % (self._schema_name, schema_path), exc_info=True)

    def __repr__(self):
        return "<gtweak.gsettings._GSettingsSchema: %s>" % self._schema_name


class GSettingsFakeSetting:
    def __init__(self):
        pass

    def get_range(self, *args, **kwargs):
        return False, []

    def get_string(self, *args, **kwargs):
        return ""

    def __getitem__(self, key):
        return ""

    def __getattr__(self, name):
        def noop(*args, **kwargs):
            pass
        return noop


class GSettingsSetting(Gio.Settings):
    def __init__(self, schema_name, schema_child_name=None, schema_dir=None, schema_path=None, schema_id=None, **options):

        if schema_dir is None:
            if schema_path is None and schema_id is None and schema_name not in _GSETTINGS_SCHEMAS:
                raise GSettingsMissingError(schema_name)

            if schema_path is not None and schema_name not in _GSETTINGS_RELOCATABLE_SCHEMAS:
                raise GSettingsMissingError(schema_name)

            if schema_path is None and schema_id is None:
                Gio.Settings.__init__(self, schema=schema_name)
            elif schema_id is not None:
                Gio.Settings.__init__(self, schema_id=schema_id)
            else:
                Gio.Settings.__init__(self, schema=schema_name, path=schema_path)
        else:
            try:
                GioSSS = Gio.SettingsSchemaSource
                schema_source = GioSSS.new_from_directory(schema_dir,
                                                          GioSSS.get_default(),
                                                          False)
                schema_obj = schema_source.lookup(schema_name, True)
                if not schema_obj:
                    raise GSettingsMissingError(schema_name)
            except GLib.GError as e:
                logging.exception("Failed to load schema from %s" % schema_dir, exc_info=e)

                raise GSettingsMissingError(schema_name)

            Gio.Settings.__init__(self, None, settings_schema=schema_obj)

        if schema_name not in _SCHEMA_CACHE:
            _SCHEMA_CACHE[schema_name] = _GSettingsSchema(schema_name, child_name=schema_child_name, schema_dir=schema_dir, **options)
            logging.debug("Caching gsettings: %s" % _SCHEMA_CACHE[schema_name])

        self._schema = _SCHEMA_CACHE[schema_name]

        if gtweak.VERBOSE:
            self.connect("changed", self._on_changed)

    def _on_changed(self, settings, key_name):
        print("Change: %s %s -> %s" % (self.props.schema, key_name, self[key_name]))

    def _setting_check_is_list(self, key):
        variant = Gio.Settings.get_value(self, key)
        return variant.get_type_string() == "as"

    def schema_get_summary(self, key):
        if key not in self._schema._schema:
            return None

        return self._schema._schema[key]["summary"]

    def schema_get_description(self, key):
        if key not in self._schema._schema:
            return None

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
            # not present
            pass

    def setting_is_in_list(self, key, value):
        assert self._setting_check_is_list(key)
        return value in self[key]


if __name__ == "__main__":
    gtweak.GSETTINGS_SCHEMA_DIR = "/usr/share/glib-2.0/schemas/"

    key = "draw-background"
    s = GSettingsSetting("org.gnome.desktop.background")
    print(s.schema_get_summary(key), s.schema_get_description(key))

    key = "disabled-extensions"
    s = GSettingsSetting("org.gnome.shell")
    assert s.setting_add_to_list(key, "foo")
    assert s.setting_remove_from_list(key, "foo")
    assert not s.setting_remove_from_list(key, "foo")
