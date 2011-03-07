from gi.repository import Gtk, Gio

class TweakSwitch(Gtk.HBox):
    def __init__(self, settings, key):
        Gtk.HBox.__init__(self)

        self._settings = settings
        lbl = Gtk.Label(self._settings.get_summary(key))
        self.pack_start(lbl, False, False, 0)

        self._sw = Gtk.Switch()
        self.pack_start(self._sw, False, False, 0)

        self._settings.gsettings.bind(key, self._sw, "active", Gio.SettingsBindFlags.DEFAULT)

        self.show_all()


