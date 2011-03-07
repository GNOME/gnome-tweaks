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

class GSettingsSetting:
    def __init__(self, schema_name):
        self.gsettings = Gio.Settings(schema_name)
        self._schema = _GSettingsSchema(schema_name)

    def get_summary(self, key):
        return self._schema._schema[key]["summary"]
        
    def get_description(self, key):
        return self._schema._schema[key]["description"]

    def get_value(self, key):
        return self.gsettings[key]

    def get_all(self, key):
        return dict(key=key, value=self.gsettings[key], **self._schema._schema[key])

if __name__ == "__main__":
    setting = GSettingsSetting("org.gnome.desktop.background")
    print setting.get_all("draw-background")
