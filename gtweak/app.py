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
from gi.repository import Gio

import gtweak 
from gtweak.tweakmodel import TweakModel
from gtweak.tweakview import TweakView
from gtweak.utils import SchemaList
from gtweak.gshellwrapper import GnomeShellFactory
        
class GnomeTweakTool(Gtk.Application):
    def __init__(self):
        Gtk.Application.__init__(self,application_id="org.gnome.TweakTool")
    
    def do_activate(self):                                           
        self.win = self.builder.get_object('main_window')
        self.win.set_position(Gtk.WindowPosition.CENTER)
        self.win.set_application(self)
        self.win.set_size_request(720, 580)
        toolbar = self.builder.get_object('toolbar')
        toolbar.get_style_context().add_class(Gtk.STYLE_CLASS_PRIMARY_TOOLBAR)
        
        model = TweakModel()
        view = TweakView(self.builder, model)
        self.builder.get_object('overview_sw').add(view.treeview)
        
        self.win.show_all()
        view.run()
        
    def do_startup(self):
        Gtk.Application.do_startup(self)
        
        self.builder = Gtk.Builder()
        assert(os.path.exists(gtweak.PKG_DATA_DIR))   
        filename = os.path.join(gtweak.PKG_DATA_DIR, 'shell.ui')
        self.builder.add_from_file(filename)
        
        appmenu = self.builder.get_object('appmenu')
        self.set_app_menu(appmenu)

        reset_action = Gio.SimpleAction.new("reset", None)
        reset_action.connect("activate", self.reset_cb)
        self.add_action(reset_action)        

        help_action = Gio.SimpleAction.new("help", None)
        help_action.connect("activate", self.help_cb)
        self.add_action(help_action)

        about_action = Gio.SimpleAction.new("about", None)
        about_action.connect("activate", self.about_cb)
        self.add_action(about_action)

        quit_action = Gio.SimpleAction.new("quit", None)
        quit_action.connect("activate", self.quit_cb)
        self.add_action(quit_action)


    def reset_cb(self, action, parameter):
        dialog = Gtk.MessageDialog(self.win,0, Gtk.MessageType.QUESTION,
                    Gtk.ButtonsType.OK_CANCEL, "Reset to Defaults")
        dialog.format_secondary_text("Reset all tweak settings to the original default state?")
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            s = SchemaList() 
            s.reset()
        dialog.destroy()
            
    def help_cb(self, action, parameter):
        print "This does nothing. It is only a demonstration."

    def about_cb(self, action, parameter):
        aboutdialog = Gtk.AboutDialog()
        aboutdialog.set_title("About GNOME Tweak Tool")
        aboutdialog.set_program_name("GNOME Tweak Tool")

        _shell = GnomeShellFactory().get_shell()
        if _shell is not None:
            aboutdialog.set_comments("GNOME Shell v%s (%s mode)" % (_shell.version, _shell.mode))
        else:
            aboutdialog.set_comments("GNOME Shell not running")

        aboutdialog.set_copyright("Copyright \xc2\xa9 2011 - 2013 John Stowers.")
        aboutdialog.set_logo_icon_name("gnome-tweak-tool")
        aboutdialog.set_website("http://live.gnome.org/GnomeTweakTool") 
        aboutdialog.set_website_label("Homepage")
        aboutdialog.set_license_type(Gtk.License.GPL_3_0)
            
        AUTHORS = [
                "John Stowers <john.stowers@gmail.com>"
                ]
 
        aboutdialog.set_authors(AUTHORS)             
        aboutdialog.connect("response", lambda w, r: aboutdialog.destroy())
        aboutdialog.show()

    def quit_cb(self, action, parameter):
        self.quit()
    
