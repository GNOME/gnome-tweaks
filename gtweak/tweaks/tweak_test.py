from __future__ import print_function

from gi.repository import Gtk

from gtweak.tweakmodel import Tweak, TweakGroup

class _TestTweak(Tweak):
    def __init__(self, name, description, **options):
        Tweak.__init__(self, name, description, **options)
        self.widget = Gtk.Label("... " + name + " ...")

class _TestButtonTweak(Tweak):
    def __init__(self, name, description, **options):
        Tweak.__init__(self, name, description, **options)
        self.widget = Gtk.Button(name)
        self.widget.connect("clicked", self._on_click)
        self._need_action = options.get("need_action")

    def _on_click(self, sender):
        if self._need_action:
            self.notify_action_required(
                    self.name,
                    Gtk.STOCK_OK,
                    lambda : print("GOT CALLBACK"))
        else:
            self.notify_error(self.name)

TWEAK_GROUPS = (
        TweakGroup(
            "Test Foo Bar",
            _TestTweak("foo bar", "does foo bar"),
            _TestTweak("foo baz", "does foo baz"),
            _TestButtonTweak("Need Action", "foo bar", need_action=True),
            _TestButtonTweak("Report Error", "foo baz", need_action=False)),
        TweakGroup(
            "Test Many Settings",
            *[_TestTweak("name: " + str(d), "desc: " + str(d)) for d in range(50)]),
)
