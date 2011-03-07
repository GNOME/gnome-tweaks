from gi.repository import Gtk, GObject

class Tweak:
    def __init__(self, name, description):
        self.name = name
        self.description = description

    @property
    def widget(self):
        raise NotImplementedError

    def search_matches(self, txt):
        return txt in self.name or txt in self.description

class TweakGroup:
    def __init__(self, name, *tweaks):
        self.name = name
        self.tweaks = [t for t in tweaks]

class _TestTweak(Tweak):
    def __init__(self, name, description):
        Tweak.__init__(self, name, description)
        self.widget = Gtk.Label("... " + name + " ...")

class TweakModel(Gtk.ListStore):
    (COLUMN_NAME,
     COLUMN_TWEAK) = range(2)

    def __init__(self):
        super(TweakModel, self).__init__(str, object)

    @property
    def tweaks(self):
        return [t for row in self for t in row[TweakModel.COLUMN_TWEAK].tweaks]

    @property
    def tweak_groups(self):
        return [row[TweakModel.COLUMN_TWEAK] for row in self]

    def load_tweaks(self):
        self.add_tweak_group(
                    TweakGroup(
                        "foo",
                        _TestTweak("foo bar", "does foo bar"),
                        _TestTweak("foo baz", "does foo baz")))
        self.add_tweak_group(
                    TweakGroup(
                        "red",
                        _TestTweak("red blue", "red blue green"),
                        _TestTweak("blue green", "orange yellow")))

    def add_tweak_group(self, tweakgroup):
        self.append([tweakgroup.name, tweakgroup])
      
    def search_matches(self, txt):
        return [t for t in self.tweaks if t.search_matches(txt)]
        
