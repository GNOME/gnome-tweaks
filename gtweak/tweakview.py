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

DEFAULT_TWEAKGROUP = gtweak.tweakmodel.TWEAK_GROUP_SHELL
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
        self._main_window = builder.get_object('main_window')

        self._main_window.props.title = gettext(self._main_window.props.title)

        self._main_window.set_size_request(740, 636)
        self._main_window.connect('destroy', Gtk.main_quit)

        self._entry_manager = EntryManager(
            builder.get_object('search_entry'),
            self._on_search,
            self._on_search_cancel)

        self._model = model
        self._model.load_tweaks()

        self.treeview = Gtk.TreeView(model=model)        
        self.treeview.props.headers_visible = False
        self.treeview.append_column(
                Gtk.TreeViewColumn(
                        "Tweak", Gtk.CellRendererText(), text=TweakModel.COLUMN_NAME))
        self.treeview.get_selection().connect("changed", self._on_selection_changed)

        #make sure the tweak background is the correct color
        ctx = builder.get_object('tweak_viewport').get_style_context ()
        provider = Gtk.CssProvider()
        provider.load_from_data ("GtkViewport {\n"
                                 "   background-color: @theme_bg_color;\n"
                                 "}\n")
        ctx.add_provider (provider,6000)

        #add all tweaks
        self._tweak_vbox = builder.get_object('tweak_vbox')
        for t in sorted(self._model.tweaks, key=_sort_tweak_widgets_by_widget_type):
            self._tweak_vbox.pack_start(t.widget, False, False, 0)
            t.set_notify_cb(self._on_tweak_notify)

        #dict of pending notifications, the key is the function to be called
        self._notification_functions = {}

    def run(self):
        self._main_window.show_all()
        self.treeview.get_selection().select_iter(
                self._model.get_tweakgroup_iter(DEFAULT_TWEAKGROUP))
        Gtk.main()

    def show_only_tweaks(self, tweaks):
        for t in self._model.tweaks:
            if t in tweaks:
                t.widget.show_all()
            else:
                t.widget.hide()

    def select_none(self):
        self.treeview.get_selection().unselect_all()

    def _on_tweak_notify_response(self, info, response, func):
        self._detail_vbox.remove(info)
        func()
        try:
            del(self._notification_functions[func])
        except KeyError:
            logging.warning("Could not remove notification function")

    def _on_tweak_notify(self, tweak, desc, error, btn, func):
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

    def _on_selection_changed(self, selection):
        t1 = datetime.datetime.now()
        model, selected = selection.get_selected()
        if selected:
            self._on_pre_selection_change()
            tweakgroup = model.get_value(selected, model.COLUMN_TWEAK)
            self.show_only_tweaks(tweakgroup.tweaks)
            self._on_post_selection_change()
        t2 = datetime.datetime.now()
        #print "TTTTTT=",t2-t1
            
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
        

