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

import os.path

from gi.repository import Gtk

import gtweak
from gtweak.tweakmodel import TweakModel
from gtweak.tweakview import TweakView

class MainWindow:
    def __init__(self):
        builder = Gtk.Builder()

        assert(os.path.exists(gtweak.PKG_DATA_DIR))

        filename = os.path.join(gtweak.PKG_DATA_DIR, 'shell.ui')
        builder.add_from_file(filename)
        
        welcome = builder.get_object('welcome_image')
        welcome.set_from_file(os.path.join(gtweak.PKG_DATA_DIR, 'welcome.png'))

        toolbar = builder.get_object('toolbar')
        toolbar.get_style_context().add_class(Gtk.STYLE_CLASS_PRIMARY_TOOLBAR)
        
        model = TweakModel()
        view = TweakView(
                    builder,
                    model)
        builder.get_object('overview_sw').add(view.treeview)

        view.run()

