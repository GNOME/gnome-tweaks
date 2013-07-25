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
import datetime

from gi.repository import Gtk, Gdk, GObject

import gtweak.tweakmodel
from gtweak.tweakmodel import TweakModel
from gtweak.utils import Notification

DEFAULT_TWEAKGROUP = gtweak.tweakmodel.TWEAK_GROUP_APPEARANCE
WIDGET_SORT_ORDER = (Gtk.Switch, Gtk.SpinButton, Gtk.ComboBox, Gtk.Box, Gtk.VBox, Gtk.HBox)

def _sort_tweak_widgets_by_widget_type(tweak):
    #for appearance tries to make small widgets be packed first, followed by larger widgets,
    #followed by widgets of the same type
    if not tweak.widget_for_size_group:
        return -1
    if tweak.widget_sort_hint != None:
        return tweak.widget_sort_hint
    try:
        return WIDGET_SORT_ORDER.index(type(tweak.widget_for_size_group))
    except ValueError:
        return len(WIDGET_SORT_ORDER) #last

class TweakView:
    def __init__(self, builder, model):
        self._notebook = builder.get_object('notebook')
        self._detail_vbox = builder.get_object('detail_vbox')

        self.headerbar = Gtk.HeaderBar()
        searchToggle = Gtk.ToggleButton()
        searchToggle.add(Gtk.Image.new_from_stock(Gtk.STOCK_FIND, Gtk.IconSize.MENU))

        top = builder.get_object('topbox')
        top.pack_start(self.headerbar, True, True, 0)
        
        self.headerbar.pack_start(searchToggle)
        leftbox = builder.get_object('leftbox')
        revealer = Gtk.Revealer();

        entry = Gtk.SearchEntry()
        self._entry_manager = EntryManager(
            entry,
            self._on_search,
            self._on_search_cancel)

        revealer.add(entry)
        leftbox.pack_start(revealer, False, True, 0)
        searchToggle.connect("toggled", self.transition, entry, revealer)
        self._model = model
        self._model.load_tweaks()
        groups = self._model._tweak_group_names.keys()
 	groups = sorted(groups)
        listbox = self.init_listbox(groups)
        leftbox.pack_start(listbox, True, True, 0)

        #make sure the tweak background is the correct color
        ctx = builder.get_object('tweak_viewport').get_style_context ()
        provider = Gtk.CssProvider()
        provider.load_from_data ("GtkViewport {\n"
                                 "   background-color: @theme_bg_color;\n"
                                 "}\n")
        ctx.add_provider (provider,6000)

        self.stack = Gtk.Stack()
        for g in groups:
            itere = self._model.get_tweakgroup_iter(g)  
            tweakgroup = self._model.get_value(itere, self._model.COLUMN_TWEAK)
            box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            for t in sorted(tweakgroup.tweaks, key=_sort_tweak_widgets_by_widget_type):            
                box.pack_start(t.widget, False, False, 5)
                t.set_notify_cb(self._on_tweak_notify)
            self.stack.add_named(box, g)
        self._tweak_vbox = builder.get_object('tweak_vbox')
        self._tweak_vbox.pack_start(self.stack, False, False, 0)
        self._on_post_selection_change()
        #dict of pending notifications, the key is the function to be called
        self._notification_functions = {}

    def run(self):
        self.stack.set_visible_child_name(DEFAULT_TWEAKGROUP)  
        self.headerbar.set_title(DEFAULT_TWEAKGROUP)
	
    def show_only_tweaks(self, tweaks):
        for t in self._model.tweaks:
            if t in tweaks:
                t.widget.show_all()
            else:
                t.widget.hide()

    def select_none(self):
        print "filter"

    def _on_tweak_notify_response(self, info, response, func):
        self._detail_vbox.remove(info)
        func()
        try:
            del(self._notification_functions[func])
        except KeyError:
            logging.warning("Could not remove notification function")

    def _on_tweak_notify(self, tweak, desc, error, btn, func, need_logout):
        #if need to log out, do this as a notification area thing, not a note inside
        #the main window
        
        if need_logout:
            notification = Notification()
            notification.show()
        
        info = Gtk.InfoBar()
        info.get_content_area().add(Gtk.Label(desc))

        if error:
            info.props.message_type = Gtk.MessageType.ERROR
        else:
            info.props.message_type = Gtk.MessageType.INFO

        if btn and func:
            if func in self._notification_functions:
                return
            self._notification_functions[func] = True
            info.add_button(btn, Gtk.ResponseType.OK)
            info.connect("response", self._on_tweak_notify_response, func)
        else:
            GObject.timeout_add_seconds(2, lambda box, widget: box.remove(widget), self._detail_vbox, info)

        self._detail_vbox.pack_end(info, False, False, 0)

        info.show_all()

    def _on_search(self, txt):
        tweaks = self._model.search_matches(txt)
        self.show_only_tweaks(tweaks)
        self.select_none()
        self._notebook.set_current_page(1)

    def _on_search_cancel(self):
        self._notebook.set_current_page(0)

    def _on_pre_selection_change(self):
        self._notebook.set_current_page(0)

    def _on_post_selection_change(self):
        self._notebook.set_current_page(1)

    def _on_selection_changed(self, lista, row):
        if row is not None:
            text = row.get_child().get_text()  
            self.stack.set_visible_child_name(text)
            self.headerbar.set_title(text)

    def init_listbox(self, values):
        listbox = Gtk.ListBox()
        for i in values:
            lbl = Gtk.Label(i)
            lbl.props.xalign = 0.0
            row = Gtk.ListBoxRow()
            listbox.add(lbl)
        widget = listbox.get_row_at_index(0)
        listbox.select_row (widget)        
        listbox.connect("row-selected", self._on_selection_changed)
        return listbox          
    
    def transition(self, btn, entry, revealer):
        if revealer.get_reveal_child():
            revealer.set_reveal_child(False) 
            entry.set_text("") 
            btn.grab_focus()      
        else:
            revealer.set_reveal_child(True)
            entry.grab_focus()


class EntryManager:

    SYMBOLIC = "-symbolic"

    def __init__(self, search_entry, search_cb, search_cancel_cb):
        self._entry = search_entry
        self._search_cb = search_cb
        self._search_cancel_cb = search_cancel_cb
        self._entry.connect("changed", self._on_changed)
        self._entry.connect("key-press-event", self._on_key_press)
        self._entry.connect("icon-release", self._on_clear_icon_release)
        self._on_changed(self._entry)

    def _search(self):
        txt = self._entry.get_text()
        if txt:
            self._search_cb(txt)

    def _search_cancel(self):
        self._search_cancel_cb()
        self._entry.set_text("")
        
    def _on_changed(self, entry):
        if not self._entry.get_text():
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
            self._search()
        elif event.keyval == Gdk.KEY_Escape:
            self._search_cancel()
    
    def _on_clear_icon_release(self, *args):
        self._search_cancel()
        

