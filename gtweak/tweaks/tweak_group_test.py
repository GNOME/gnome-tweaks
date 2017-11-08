# Copyright (c) 2011 John Stowers
# SPDX-License-Identifier: GPL-3.0+
# License-Filename: LICENSES/GPL-3.0

from gi.repository import Gtk, Gdk

from gtweak.tweakmodel import Tweak
from gtweak.widgets import ListBoxTweakGroup, Title, build_label_beside_widget

class _TestInfoTweak(Gtk.Box, Tweak):
    def __init__(self, name, description, **options):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.HORIZONTAL)
        Tweak.__init__(self, name, description, **options)

        build_label_beside_widget(
                        name,
                        Gtk.Button(options.get("_test_button_name",name)),
                        info=options.get("_tweak_info"),
                        warning=options.get("_tweak_warning"),
                        hbox=self)

class _TestTweak(Gtk.Box, Tweak):
    def __init__(self, name, description, **options):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.HORIZONTAL)
        Tweak.__init__(self, name, description, **options)
        self.add(Gtk.Label("... " + name + " ..."))

class _TestButtonTweak(Gtk.Box, Tweak):
    def __init__(self, name, description, **options):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.HORIZONTAL)
        Tweak.__init__(self, name, description, **options)
        widget = Gtk.Button(name)
        widget.connect("clicked", self._on_click)
        self.add(widget)
        self._need_action = options.get("_need_action")
        self._need_logout = options.get("_need_logout")

    def _on_click(self, sender):
        if self._need_action:
            self.notify_information(self.name)
        elif self._need_logout:
            self.notify_logout()

css_provider = Gtk.CssProvider()
css_provider.load_from_data("""
.list-row.tweak#tweak-test-foo {
        background-color: red;
}
.list-row.tweak.title#title-tweak-test {
        background-color: blue;
}
.list.tweak-group#group-tweak-test {
        background-color: green;
}
""")
screen = Gdk.Screen.get_default()
context = Gtk.StyleContext()
context.add_provider_for_screen(
            screen,
            css_provider,
            1 + Gtk.STYLE_PROVIDER_PRIORITY_USER)

TWEAK_GROUPS = [
    ListBoxTweakGroup(
        "Test Many Settings",
        *[_TestTweak("name: " + str(d), "desc: " + str(d)) for d in range(10)],
        uid="group-tweak-test"),
    ListBoxTweakGroup(
        "Test Settings",
        _TestTweak("foo bar", "does foo bar", uid="tweak-test-foo"),
        _TestTweak("foo baz", "does foo baz"),
        _TestInfoTweak("long string "*10, "long description "*10, _test_button_name="short"),
        _TestInfoTweak("foo info", "info widget", _tweak_info="Information"),
        _TestInfoTweak("foo warning", "info widget", _tweak_warning="Warning"),
        Title("Test Notifications", "", uid="title-tweak-test"),
        _TestButtonTweak("Shows Information", "foo bar", _need_action=True),
        _TestButtonTweak("Needs Logout", "foo bar log", _need_logout=True)),

    ListBoxTweakGroup(
        "Unicode Test",
        Title("Words", "", uid="title-tweak-test"),
        *[_TestTweak( str(d), str(d)) for d in ["Muñoz",
                                                "Español",
                                                "größer",
                                                "jünger",
                                                "grün",
                                                "счастье",
                                                "سعادة"]]),
]

