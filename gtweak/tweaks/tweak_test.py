from gi.repository import Gtk

from gtweak.tweakmodel import Tweak, TweakGroup

class _TestTweak(Tweak):
    def __init__(self, name, description):
        Tweak.__init__(self, name, description)
        self.widget = Gtk.Label("... " + name + " ...")

TWEAK_GROUPS = (
        TweakGroup(
            "foo",
            _TestTweak("foo bar", "does foo bar"),
            _TestTweak("foo baz", "does foo baz")),
        TweakGroup(
            "red",
            _TestTweak("red blue", "red blue green"),
            _TestTweak("blue green", "orange yellow"))
)
