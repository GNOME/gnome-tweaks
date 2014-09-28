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
import logging
import datetime

from gi.repository import Gtk, Gdk, GObject

import gtweak.tweakmodel
from gtweak.tweakmodel import TweakModel
from gtweak.widgets import Title

class Window(Gtk.ApplicationWindow):

    def __init__(self, app, model):
        Gtk.ApplicationWindow.__init__(self,
                                       application=app,
                                       show_menubar=False)
        
        self.set_size_request(950, 680)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_icon_name("gnome-tweak-tool")
        
        self.hsize_group = Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL)

        main_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        left_box = self.sidebar()
        right_box = self.main_content()
        separator = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)
        
        titlebar = self.titlebar()
        self.set_titlebar(titlebar)

        main_box.pack_start(left_box, False, False, 0)
        main_box.pack_start(separator, False, False, 0)
        main_box.pack_start(right_box, True, True, 0)
        
        self.load_css()      
        self._model = model
        self._model.load_tweaks(self)
        self.load_model_data()

        Gtk.Settings.get_default().connect("notify::gtk-decoration-layout",
                                          self._update_decorations);

        self.connect("key-press-event", self._on_key_press)
        self.add(main_box)
    
    def titlebar(self):

        header = Gtk.Box()

        left_header = Gtk.HeaderBar()
        left_header.props.show_close_button = True
        right_header = Gtk.HeaderBar()
        right_header.props.show_close_button = True

        self._left_header = left_header;
        self._right_header = right_header;

        left_header.get_style_context().add_class("titlebar")
        left_header.get_style_context().add_class("tweak-titlebar-left")
        right_header.get_style_context().add_class("titlebar")
        right_header.get_style_context().add_class("tweak-titlebar-right")

        self._update_decorations (Gtk.Settings.get_default(), None)

        self.title = Gtk.Label(label="")
        self.title.get_style_context().add_class("title")
        right_header.set_custom_title(self.title)

        icon = Gtk.Image()
        icon.set_from_icon_name("edit-find-symbolic",Gtk.IconSize.MENU)
        self.button = Gtk.ToggleButton()
        self.button.add(icon)
        self.button.connect("toggled", self._on_find_toggled)
        self.button.props.valign = Gtk.Align.CENTER
        self.button.get_style_context().add_class("image-button")
        left_header.pack_start(self.button)

        lbl = Gtk.Label(label=_("Tweaks"))
        lbl.get_style_context().add_class("title")
        left_header.set_custom_title(lbl)

        header.pack_start(left_header, False, False, 0)
        header.pack_start(Gtk.Separator(orientation=Gtk.Orientation.VERTICAL), False, False, 0)
        header.pack_start(right_header, True, True, 0)
        
        self.hsize_group.add_widget(left_header)

        return header
        
        
    def sidebar(self):
        left_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        
        self.entry = Gtk.SearchEntry(placeholder_text=_("Search Tweaks..."))
        self.entry.connect("search-changed", self._on_search)
        
        self.searchbar = Gtk.SearchBar()
        self.searchbar.add(self.entry)
        self.searchbar.props.hexpand = False
        
        self.listbox = Gtk.ListBox()
        self.listbox.get_style_context().add_class("tweak-categories")
        self.listbox.set_size_request(200,-1)
        self.listbox.connect("row-selected", self._on_select_row)
        self.listbox.set_header_func(self._list_header_func, None)
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER,
                          Gtk.PolicyType.AUTOMATIC)
        scroll.add(self.listbox)
        
        left_box.pack_start(self.searchbar, False, False, 0)
        left_box.pack_start(scroll, True, True, 0)
        
        self.hsize_group.add_widget(left_box)

        return left_box
        
    def main_content(self):        
        right_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        
        #GRR why can I not put margin in the CSS of a GtkStack
        self.stack = Gtk.Stack()
        self.stack.get_style_context().add_class("main-container")
        self.stack.props.margin = 20
    
        right_box.pack_start(self.stack, True, True, 0)
        
        return right_box

    def load_css(self):
        css_provider = Gtk.CssProvider()
        css_provider.load_from_path(
                        os.path.join(gtweak.PKG_DATA_DIR, 'shell.css'))
        screen = Gdk.Screen.get_default()
        context = Gtk.StyleContext()
        context.add_provider_for_screen(screen, css_provider,
                                Gtk.STYLE_PROVIDER_PRIORITY_USER)

    def load_model_data(self):

        def _make_items_listbox(text):
            lbl = Gtk.Label(label=text, xalign=0.0)
            lbl.set_name('row')
            row = Gtk.ListBoxRow()
            row.get_style_context().add_class("tweak-category")
            row.add(lbl)
            return row

        groups = self._model._tweak_group_names.keys()
        groups = sorted(groups)

        for g in groups:
            row = _make_items_listbox(g)
            self.listbox.add(row)
            tweakgroup = self._model.get_value(
                                self._model.get_tweakgroup_iter(g), 
                                self._model.COLUMN_TWEAK)
            scroll = Gtk.ScrolledWindow()
            scroll.add(tweakgroup)
            self.stack.add_named(scroll, g)

        widget = self.listbox.get_row_at_index(0)
        self.listbox.select_row (widget)

    def _list_filter_func(self, row, user_data):
        lbl = row.get_child()
        if lbl.get_text() in user_data:
            return row
    
    def _list_header_func(self, row, before, user_data):
        if before and not row.get_header():
            row.set_header (Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL))

    def _update_decorations(self, settings, pspec):
        layout_desc = settings.props.gtk_decoration_layout;
        tokens = layout_desc.split(":", 2)
        if tokens != None:
                self._right_header.props.decoration_layout = ":" + tokens[1]
                self._left_header.props.decoration_layout = tokens[0]

    def _on_key_press(self, widget, event):
        keyname = Gdk.keyval_name(event.keyval)
        if keyname == 'Escape':
            self.button.set_active(False)
        if event.state and Gdk.ModifierType.CONTROL_MASK:
            if keyname == 'f':
                self.button.set_active(True)

    def _on_list_changed(self, group):
        self.listbox.set_filter_func(self._list_filter_func, group)
        selected = self.listbox.get_selected_row().get_child().get_text()
        if group and not selected in group:
            index =  sorted(self._model._tweak_group_names.keys()).index(group[0])
            row = self.listbox.get_row_at_index(index)
            self.listbox.select_row(row)

    def _on_search(self, entry):
        txt = entry.get_text().decode("utf-8","ignore").lower()
        tweaks, group = self._model.search_matches(txt)
        self.show_only_tweaks(tweaks)        
        self._on_list_changed(group)
        
    def _on_select_row(self, listbox, row):
        if row:
            group = row.get_child().get_text()
            self.stack.set_visible_child_name(group)
            self.title.set_text(group)

    def _on_find_toggled(self, btn):
         if self.searchbar.get_search_mode():
             self.searchbar.set_search_mode(False)
             self.entry.set_text("")
         else:
            self.searchbar.set_search_mode(True)
            self.entry.grab_focus()

    def show_only_tweaks(self, tweaks):
        for t in self._model.tweaks:
            if t in tweaks:
                t.show_all()
            else:
                t.hide()
