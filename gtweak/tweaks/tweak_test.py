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

class _TestInfoTweak(Tweak):
    def __init__(self, name, description, **options):
        Tweak.__init__(self, name, description, **options)

        self.widget = build_label_beside_widget(
                        name,
                        Gtk.Button(options.get("test_button_name",name)),
                        info=options.get("tweak_info"),
                        warning=options.get("tweak_warning"))

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
        self._action_error = options.get("action_error")

    def _on_click(self, sender):
        if self._need_action:
            self.notify_action_required(
                    self.name,
                    Gtk.STOCK_OK,
                    lambda : print("GOT CALLBACK"))
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
    _TestInfoTweak("long string "*10, "long description "*10, test_button_name="short",group_name=group_name),
    _TestInfoTweak("foo info", "info widget", tweak_info="Information", group_name=group_name),
    _TestInfoTweak("foo warning", "info widget", tweak_warning="Warning", group_name=group_name),
    _TestButtonTweak("Need Action", "foo bar", need_action=True, group_name=group_name),
    _TestButtonTweak("Report Error", "foo baz", action_error=True, group_name=group_name),
    _TestButtonTweak("Report Info", "foo bob", action_error=False, group_name=group_name),
)

