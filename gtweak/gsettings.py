import os.path
import xml.dom.minidom

from gi.repository import Gio

class _GSettingsSchema:
    def __init__(self, schema_name, schema_dir="/home/john/GNOME/install/share/glib-2.0/schemas/", schema_file=None):
        if not schema_file:
            schema_file = schema_dir + schema_name + ".gschema.xml"
        
        assert(os.path.exists(schema_file))
        self._schema = {}
        
        try:
            dom = xml.dom.minidom.parse(schema_file)
            for schema in dom.getElementsByTagName("schema"):
                for key in schema.getElementsByTagName("key"):
                    self._schema[key.getAttribute("name")] = {
                            "summary"       :   key.getElementsByTagName("summary")[0].childNodes[0].data,
                            "description"   :   key.getElementsByTagName("description")[0].childNodes[0].data}
        except:
            import traceback
            traceback.print_exc()

_SCHEMA_CACHE = {}

class GSettingsSetting(Gio.Settings):
    def __init__(self, schema_name):
        Gio.Settings.__init__(self, schema_name)
        if schema_name not in _SCHEMA_CACHE:
            _SCHEMA_CACHE[schema_name] = _GSettingsSchema(schema_name)
        self._schema = _SCHEMA_CACHE[schema_name]

    def schema_get_summary(self, key):
        return self._schema._schema[key]["summary"]
        
    def schema_get_description(self, key):
        return self._schema._schema[key]["description"]

    def schema_get_all(self, key):
        return self._schema._schema[key]

if __name__ == "__main__":
    key = "draw-background"
    setting = GSettingsSetting("org.gnome.desktop.background")
    print setting.schema_get_summary(key),setting.schema_get_description(key)
