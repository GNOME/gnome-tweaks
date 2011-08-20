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

import logging
import glob
import os.path

import gtweak

from gi.repository import Gtk

TWEAK_GROUP_FONTS = _("Fonts")
TWEAK_GROUP_THEME = _("Theme")
TWEAK_GROUP_DESKTOP = _("Desktop")
TWEAK_GROUP_WINDOWS = _("Windows")

LOG = logging.getLogger(__name__)

class Tweak:
    def __init__(self, name, description, **options):
        self.name = name
        self.description = description
        self.group_name = options.get("group_name",_("Miscellaneous"))

        self._search_cache = None

        #FIXME: I would have rather done this as a GObject signal, but it
        #would prohibit other tweaks from inheriting from GtkWidgets
        self._notify_cb = None

    @property
    def widget(self):
        raise NotImplementedError

    @property
    def widget_for_size_group(self):
        return None

    def search_matches(self, txt):
        if self._search_cache == None:
            self._search_cache = set([i.strip(" .,\n'\"").lower() for j in (
                    self.name.split(' '),self.description.split(' ')) for i in j])

        return txt.strip().lower() in self._search_cache

    def set_notify_cb(self, func):
        self._notify_cb = func

    def notify_action_required(self, desc, btn, func, error=False):
        if self._notify_cb:
            self._notify_cb(self, desc, error, btn, func)

    def notify_error(self, desc):
        if self._notify_cb:
            self._notify_cb(self, desc, True, None, None)

    def notify_info(self, desc):
        if self._notify_cb:
            self._notify_cb(self, desc, False, None, None)

class TweakGroup:
    def __init__(self, name, *tweaks):
        self.name = name
        self.tweaks = []

        self._sg = Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL)
        self._sg.props.ignore_hidden = True

        self.set_tweaks(*tweaks)

    def set_tweaks(self, *tweaks):
        self.tweaks += [t for t in tweaks]

        for t in tweaks:
            if t.widget_for_size_group:
                self._sg.add_widget(t.widget_for_size_group)

class TweakModel(Gtk.ListStore):
    (COLUMN_NAME,
     COLUMN_TWEAK) = range(2)

    def __init__(self):
        super(TweakModel, self).__init__(str, object)
        self._tweak_dir = gtweak.TWEAK_DIR
        assert(os.path.exists(self._tweak_dir))

        self.set_sort_column_id(self.COLUMN_NAME, Gtk.SortType.ASCENDING)

        # map of tweakgroup.name -> tweakgroup
        self._tweak_group_names = {}

    @property
    def tweaks(self):
        return [t for row in self for t in row[TweakModel.COLUMN_TWEAK].tweaks]

    @property
    def tweak_groups(self):
        return [row[TweakModel.COLUMN_TWEAK] for row in self]

    def load_tweaks(self):
        if 1:
            tweak_files = [
                    os.path.splitext(os.path.split(f)[-1])[0]
                        for f in glob.glob(os.path.join(self._tweak_dir, "tweak_*.py"))]
        else:
            tweak_files = ["tweak_test"]

        if not gtweak.ENABLE_TEST:
            try:
                tweak_files.remove("tweak_test")
            except ValueError:
                pass
        
        groups = []
        tweaks = []

        mods = __import__("gtweak.tweaks", globals(), locals(), tweak_files, 0)
        for mod in [getattr(mods, file_name) for file_name in tweak_files]:
            groups.extend( getattr(mod, "TWEAK_GROUPS", []) )
            tweaks.extend( getattr(mod, "TWEAKS", []) )

        for g in groups:
            self.add_tweak_group(g)

        for t in tweaks:
            self.add_tweak_auto_to_group(t)

    def add_tweak_group(self, tweakgroup):
        if tweakgroup.name in self._tweak_group_names:
            LOG.critical("Tweak group named: %s already exists" % tweakgroup.name)
            return

        self.append([tweakgroup.name, tweakgroup])
        self._tweak_group_names[tweakgroup.name] = tweakgroup

    def add_tweak_auto_to_group(self, tweak):
        name = tweak.group_name
        try:
            group = self._tweak_group_names[name]
        except KeyError:
            group = TweakGroup(name)
            self.add_tweak_group(group)

        group.set_tweaks(tweak)
      
    def search_matches(self, txt):
        return [t for t in self.tweaks if t.search_matches(txt)]
        
