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

    def show_all_tweaks(self):
        map(Gtk.Widget.show_all, [t.widget for t in self.tweaks])

    def hide_all_tweaks(self):
        map(Gtk.Widget.hide, [t.widget for t in self.tweaks])
        
    def get_tweak_widgets(self):
        return [t.widget for t in self.tweaks]

class _TestTweak(Tweak):
    def __init__(self, name, description):
        Tweak.__init__(self, name, description)
        self.widget = Gtk.Label("... " + name + " ...")

class TweakModel(Gtk.ListStore):
    (COLUMN_NAME,
     COLUMN_TWEAK) = range(2)

    def __init__(self):
        super(TweakModel, self).__init__(str, object)

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

    #You almost have it! The way to do nested list comprehensions is to put the for statements in the same order as they would go in regular nested for statements.
    #
    #Thus, this
    #
    #for inner_list in outer_list:
    #    for item in inner_list:
    #        ...
    #corresponds to
    #
    #[... for inner_list in outer_list for item in inner_list]        
    def foreach_tweak_widget(self, func, *args):
        for row in self:
            for t in row[TweakModel.COLUMN_TWEAK].get_tweak_widgets():
                func(t, *args)
                
    def get_matching(self, txt):
        m = []
        for row in self:
            for t in row[TweakModel.COLUMN_TWEAK].tweaks:
                if t.search_matches(txt):
                    m.append(t)
        return m
        
