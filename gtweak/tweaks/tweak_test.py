from gi.repository import Gtk

from gtweak.tweakmodel import Tweak, TweakGroup

class _TestTweak(Tweak):
    def __init__(self, name, description):
        Tweak.__init__(self, name, description)
        self.widget = Gtk.Label("... " + name + " ...")

TWEAK_GROUPS = (
        TweakGroup(
            "Test Foo Bar",
            _TestTweak("foo bar", "does foo bar"),
            _TestTweak("foo baz", "does foo baz")),
        TweakGroup(
            "Test Many Settings",
            *[_TestTweak("name: " + str(d), "desc: " + str(d)) for d in range(50)]),
)
