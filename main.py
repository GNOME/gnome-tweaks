#!/usr/bin/env python

import os.path

from gi.repository import Gtk, Gdk

from tweakmodel import TweakModel

class TweakView(Gtk.TreeView):
    def __init__(self, pre_selection_change_cb, post_selection_change_cb, *args, **kwargs):
        super(TweakView, self).__init__(*args, **kwargs)

        self._pre_selection_change_cb = pre_selection_change_cb
        self._post_selection_change_cb = post_selection_change_cb
        
        self.props.headers_visible = False
        column = Gtk.TreeViewColumn("Tweak", Gtk.CellRendererText(), text=TweakModel.COLUMN_NAME)
        self.append_column(column)
        
        self.get_selection().connect("changed", self._on_selection_changed)
        
    def _on_selection_changed(self, selection):
        model, selected = selection.get_selected()
        if selected:
            self._pre_selection_change_cb()
            
            #apparently iters do not persist over iteration, so use treepaths instead
            path_selected = model.get_path(selected)
            #hide other tweakgroups
            root = model.get_iter_first()
            while root:
                if model.get_path(root) != path_selected:
                    tweakgroup = model.get_value(root, model.COLUMN_TWEAK)
                    print "hide", tweakgroup.name
                    tweakgroup.hide_all_tweaks()
                root = model.iter_next(root)
            #show selected
            tweakgroup = model.get_value(selected, model.COLUMN_TWEAK)
            print "show", tweakgroup.name
            tweakgroup.show_all_tweaks()
            
            self._post_selection_change_cb()
            
    def add_tweak_widget(self, tweak):
        pass
        

class EntryManager:

    SYMBOLIC = ""#"-symbolic"

    def __init__(self, search_entry, search_cb):
        self._entry = search_entry
        self._search_cb = search_cb
        self._entry.props.secondary_icon_name = "edit-find" + EntryManager.SYMBOLIC
        self._entry.connect("changed", self._on_changed)
        self._entry.connect("key-press-event", self._on_key_press)
        self._entry.connect("icon-release", self._on_clear_icon_release)

        self._entry_filter = ""
        
    def _on_changed(self, entry):
        txt = self._entry.get_text()
        if txt == self._entry_filter:
            return
        
        self._entry_filter = txt
        if not self._entry_filter:
            self._entry.set_properties(
                    secondary_icon_name="edit-find" + EntryManager.SYMBOLIC,
                    secondary_icon_activatable=False,
                    secondary_icon_sensitive=False)
        else:
            self._entry.set_properties(
                    secondary_icon_name="edit-clear" + EntryManager.SYMBOLIC,
                    secondary_icon_activatable=True,
                    secondary_icon_sensitive=True)
    
    def _on_key_press(self, entry, event):
        if event.keyval == Gdk.KEY_Return:
            self._search_cb(self._entry.get_text())
        elif event.keyval == Gdk.KEY_Escape:
            self._entry.set_text("")
    
    def _on_clear_icon_release(self, *args):
        self._entry.set_text("")

class MainWindow:
    def __init__(self):
        self._builder = Gtk.Builder()

        filename = os.path.join('data', 'shell.ui')
        self._builder.add_from_file(filename)
        
        welcome = self._builder.get_object('welcome_image')
        welcome.set_from_file(os.path.join('data', 'welcome2.png'))
        
        self._model = TweakModel()
        self._model.load_tweaks()
        
        view = TweakView(
                    self._on_pre_selection_change,
                    self._on_post_selection_change,
                    model=self._model)
        self._builder.get_object('overview_sw').add(view)
        self._notebook = self._builder.get_object('notebook')
        
        self._tweak_box = self._builder.get_object('tweak_vbox')
        self._model.foreach_tweak_widget(lambda w, box: box.pack_start(w, False, False, 0), self._tweak_box)
        
        EntryManager(
            self._builder.get_object('search_entry'),
            self._on_search)

        window = self._builder.get_object('main_window')
        window.set_size_request(640, 480)
        window.connect('destroy', Gtk.main_quit)
        window.show_all()
        
    def _on_search(self, txt):
        print "SEARCH", txt
        print self._model.get_matching(txt)

    def _on_pre_selection_change(self):
        print "pre -", self._notebook.get_current_page()
        self._notebook.set_current_page(0)
        
        #if on welcome screen, switch to main page (only happens once)
        if self._notebook.get_current_page() == 0:
            self._notebook.set_current_page(1)

    def _on_post_selection_change(self):
        self._notebook.set_current_page(1)
        print "post -", self._notebook.get_current_page()

    def run(self):
        Gtk.main()

if __name__ == '__main__':
    MainWindow().run()
