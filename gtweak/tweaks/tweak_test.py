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

from gtweak.tweakmodel import Tweak, TweakGroup
from gtweak.widgets import build_label_beside_widget

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
        self._action_error = options.get("_action_error")
        self._need_logout = options.get("_need_logout")

    def _on_click(self, sender):
        if self._need_action:
            self.notify_action_required(
                    self.name,
                    Gtk.STOCK_OK,
                    lambda : print("GOT CALLBACK"))
        elif self._need_logout:
            self.notify_action_required(
                    self.name,
                    Gtk.STOCK_OK,
                    func=None,
                    need_logout=True,
            )
        else:
            if self._action_error:
                self.notify_error(self.name)
            else:
                self.notify_info(self.name)

TWEAK_GROUPS = (
    TweakGroup(
        "Test Settings Group",
        *[_TestTweak("name: " + str(d), "desc: " + str(d)) for d in range(50)]),
)

group_name = "Test Settings"

TWEAKS = (
    _TestTweak("foo bar", "does foo bar", group_name=group_name),
    _TestTweak("foo baz", "does foo baz", group_name=group_name),
    _TestInfoTweak("long string "*10, "long description "*10, _test_button_name="short",group_name=group_name),
    _TestInfoTweak("foo info", "info widget", _tweak_info="Information", group_name=group_name),
    _TestInfoTweak("foo warning", "info widget", _tweak_warning="Warning", group_name=group_name),
    _TestButtonTweak("Need Action", "foo bar", _need_action=True, group_name=group_name),
    _TestButtonTweak("Report Error", "foo baz", _action_error=True, group_name=group_name),
    _TestButtonTweak("Report Info", "foo bob", _action_error=False, group_name=group_name),
    _TestButtonTweak("Need Log Out", "foo bar log", _need_logout=True, group_name=group_name),
)

