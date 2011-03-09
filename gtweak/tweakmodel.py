import glob
import os.path

import gtweak

from gi.repository import Gtk

class Tweak:
    def __init__(self, name, description, **options):
        self.name = name
        self.description = description
        self.size_group = options.get('size_group')

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
        return txt in self.name or txt in self.description

    def set_notify_cb(self, func):
        self._notify_cb = func

    def notify_action_required(self, desc, btn, func):
        if self._notify_cb:
            self._notify_cb(self, desc, btn, func)

    def notify_error(self, desc):
        if self._notify_cb:
            self._notify_cb(self, desc, None, None)

class TweakGroup:
    def __init__(self, name, *tweaks):
        self.name = name
        self.tweaks = [t for t in tweaks]

        for t in tweaks:
            if t.size_group and t.widget_for_size_group:
                t.size_group.add_widget(t.widget_for_size_group)

class TweakModel(Gtk.ListStore):
    (COLUMN_NAME,
     COLUMN_TWEAK) = range(2)

    def __init__(self):
        super(TweakModel, self).__init__(str, object)
        self._tweak_dir = gtweak.TWEAK_DIR
        assert(os.path.exists(self._tweak_dir))

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
        
        mods = __import__("gtweak.tweaks", globals(), locals(), tweak_files, 0)
        for mod in [getattr(mods, file_name) for file_name in tweak_files]:
            for group in mod.TWEAK_GROUPS:
                self.add_tweak_group(group)

    def add_tweak_group(self, tweakgroup):
        self.append([tweakgroup.name, tweakgroup])
      
    def search_matches(self, txt):
        return [t for t in self.tweaks if t.search_matches(txt)]
        
