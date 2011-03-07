from gi.repository import Gtk, Gio

class TweakSwitch(Gtk.HBox):
    def __init__(self, settings, key):
        Gtk.HBox.__init__(self)

        self._settings = settings
        lbl = Gtk.Label(self._settings.schema_get_summary(key))
        lbl.props.xalign = 0.0
        self.pack_start(lbl, True, False, 0)

        self._sw = Gtk.Switch()
        self.pack_start(self._sw, False, False, 0)

        self._settings.bind(key, self._sw, "active", Gio.SettingsBindFlags.DEFAULT)

        self.show_all()


