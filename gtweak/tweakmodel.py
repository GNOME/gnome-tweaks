import glob
import os.path

import gtweak

from gi.repository import Gtk

class Tweak:
    def __init__(self, name, description):
        self.name = name
        self.description = description

    @property
    def widget(self):
        raise NotImplementedError

    @property
    def widget_for_size_group(self):
        return None

    def search_matches(self, txt):
        return txt in self.name or txt in self.description

class TweakGroup:
    def __init__(self, name, *tweaks, **options):
        self.name = name
        self.tweaks = [t for t in tweaks]

        self.enable_size_group = options.get('size_group')

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
        
