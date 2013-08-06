# This file is part of gnome-tweak-tool.
#
# Copyright (c) 2011 John Stowers
#
# gnome-tweak-tool is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# gnome-tweak-tool is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with gnome-tweak-tool.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import print_function

from gi.repository import Gtk

from gtweak.tweakmodel import Tweak
from gtweak.widgets import ListBoxTweakGroup, build_label_beside_widget

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

TWEAK_GROUPS = [
    ListBoxTweakGroup(
        "Test Many Settings",
        *[_TestTweak("name: " + str(d), "desc: " + str(d)) for d in range(50)]),
    ListBoxTweakGroup(
        "Test Settings",
        _TestTweak("foo bar", "does foo bar"),
        _TestTweak("foo baz", "does foo baz"),
        _TestInfoTweak("long string "*10, "long description "*10, _test_button_name="short"),
        _TestInfoTweak("foo info", "info widget", _tweak_info="Information"),
        _TestInfoTweak("foo warning", "info widget", _tweak_warning="Warning"),
        _TestButtonTweak("Notify Information", "foo bar", _need_action=True),
        _TestButtonTweak("Notify Logout", "foo bar log", _need_logout=True))
]

