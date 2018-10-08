# Copyright (c) 2011 John Stowers
# SPDX-License-Identifier: GPL-3.0+
# License-Filename: LICENSES/GPL-3.0

import logging
import glob
import os.path

import gtweak
from gtweak.utils import SchemaList, LogoutNotification, Notification
from gi.repository import Gtk, GLib

def N_(x): return x

LOG = logging.getLogger(__name__)

def string_for_search(s):
    return GLib.utf8_casefold(GLib.utf8_normalize(s, -1, GLib.NormalizeMode.ALL), -1)


class Tweak(object):

    main_window = None
    widget_for_size_group = None
    extra_info = ""

    def __init__(self, name, description, **options):
        self.name = name or ""
        self.description = description or ""
        self.uid = options.get("uid", self.__class__.__name__)
        self.group_name = options.get("group_name", _("Miscellaneous"))
        self.loaded = options.get("loaded", True)
        self.widget_sort_hint = None

        self._search_cache = None

    def search_matches(self, txt):
        if self._search_cache is None:
            self._search_cache = string_for_search(self.name) + " " + \
				 string_for_search(self.description)
            try:
                self._search_cache += " " + string_for_search(self.extra_info)
            except:
                LOG.warning("Error adding search info", exc_info=True)
        return txt in self._search_cache

    def notify_logout(self):
        self._logoutnotification = LogoutNotification()

    def notify_information(self, summary, desc=""):
        self._notification = Notification(summary, desc)


class TweakGroup(object):

    main_window = None

    def __init__(self, name, *tweaks, **options):
        self.name = name
        self.titlebar_widget = None
        self.tweaks = [t for t in tweaks if t.loaded]
        self.uid = options.get('uid', self.__class__.__name__)

    def add_tweak(self, tweak):
        if tweak.loaded:
            self.tweaks.append(tweak)
            return True


class TweakModel(Gtk.ListStore):
    (COLUMN_NAME,
     COLUMN_TWEAK) = list(range(2))

    def __init__(self):
        super(TweakModel, self).__init__(str, object)
        self._tweak_dir = gtweak.TWEAK_DIR
        assert(os.path.exists(self._tweak_dir))

        self.set_sort_column_id(self.COLUMN_NAME, Gtk.SortType.ASCENDING)

        # map of tweakgroup.name -> tweakgroup
        self._tweak_group_names = {}
        self._tweak_group_iters = {}

    @property
    def tweaks(self):
        return (t for row in self for t in row[TweakModel.COLUMN_TWEAK].tweaks)

    @property
    def tweak_groups(self):
        return (row[TweakModel.COLUMN_TWEAK] for row in self)

    def load_tweaks(self, main_window):
        tweak_files = [
                os.path.splitext(os.path.split(f)[-1])[0]
                    for f in glob.glob(os.path.join(self._tweak_dir, "tweak_group_*.py"))]

        if not gtweak.ENABLE_TEST:
            try:
                tweak_files.remove("tweak_group_test")
            except ValueError:
                pass

        groups = []
        tweaks = []

        mods = __import__("gtweak.tweaks", globals(), locals(), tweak_files, 0)
        for mod in [getattr(mods, file_name) for file_name in tweak_files]:
            groups.extend( getattr(mod, "TWEAK_GROUPS", []))

        schemas = SchemaList()

        for g in groups:
            g.main_window = main_window
            if g.tweaks:
                self.add_tweak_group(g)
                for i in g.tweaks:
                    i.main_window = main_window
                    try:
                        schemas.insert(i.key_name, i.schema_name)
                    except:
                        pass

    def add_tweak_group(self, tweakgroup):
        if tweakgroup.name in self._tweak_group_names:
            LOG.critical("Tweak group named: %s already exists" % tweakgroup.name)
            return

        _iter = self.append([gettext(tweakgroup.name), tweakgroup])
        self._tweak_group_names[tweakgroup.name] = tweakgroup
        self._tweak_group_iters[tweakgroup.name] = _iter

    def search_matches(self, txt):
        tweaks = []
        groups = []

        for g in self.tweak_groups:
            for t in g.tweaks:
                if t.search_matches(txt):
                    tweaks.append(t)
                    if g.name not in groups:
                        groups.append(g.name)
        return tweaks, groups

    def get_tweakgroup_iter(self, name):
        return self._tweak_group_iters[name]
