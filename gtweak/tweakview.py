# Copyright (c) 2011 John Stowers
# SPDX-License-Identifier: GPL-3.0+
# License-Filename: LICENSES/GPL-3.0

import os.path
from typing import List

from gi.repository import Adw, Gtk, Gdk, GObject
import gtweak
import gtweak.widgets 
import gtweak.tweakmodel
from gtweak.tweakmodel import TweakModel, string_for_search

from gtweak.tweaks.tweak_group_appearance import TWEAK_GROUP as AppearanceTweaks
from gtweak.tweaks.tweak_group_font import TWEAK_GROUP as FontTweaks
from gtweak.tweaks.tweak_group_mouse import TWEAK_GROUP as MouseTweaks
from gtweak.tweaks.tweak_group_keyboard import TWEAK_GROUP as KeyboardTweaks
from gtweak.tweaks.tweak_group_sound import TWEAK_GROUP as SoundTweaks, show_sound_tweaks
from gtweak.tweaks.tweak_group_windows import TWEAK_GROUP as WindowTweaks
from gtweak.tweaks.tweak_group_startup import TWEAK_GROUP as StartupApplicationTweaks

tweaks = [ 
    MouseTweaks,
    KeyboardTweaks,
    FontTweaks,
    AppearanceTweaks,
    WindowTweaks,
    StartupApplicationTweaks,
    SoundTweaks
]


@Gtk.Template(filename=os.path.join(gtweak.PKG_DATA_DIR, "tweaks.ui"))
class Window(Adw.ApplicationWindow):
    __gtype_name__ = "GTweakWindow"

    main_box = Gtk.Template.Child()
    listbox = Gtk.Template.Child()
    right_box = Gtk.Template.Child()
    header = Gtk.Template.Child()
    main_content_scroll = Gtk.Template.Child()
    main_leaflet = Gtk.Template.Child()
    main_stack = Gtk.Template.Child()
    left_box = Gtk.Template.Child()
    searchbar = Gtk.Template.Child()
    entry = Gtk.Template.Child()
    list_box_row_sound = Gtk.Template.Child()

    def __init__(self, app: Adw.Application, model: TweakModel):
        super().__init__(application=app, show_menubar=False)
        self.set_default_size(980, 640)
        self.set_size_request(-1, 300)
        self.set_icon_name(gtweak.APP_ID)

        for tweak in tweaks:
            model.add_tweak_group(tweak, self)
            if tweak.name:
              self.main_stack.add_named(tweak, tweak.name)

        self._setup_header()
        self._setup_sidebar()
        self._setup_mainbox()
        self._setup_sizegroups()

        self._load_css()
        self._model = model

        self._setup_shortcut()
        self.searchbar.set_key_capture_widget(self)


    def _setup_header(self):
        self.hsize_group = Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL)
        self.menu_btn = Gtk.MenuButton()

        header = self.header
        header.set_transition_type(Adw.LeafletTransitionType.SLIDE)

        left_header = Adw.HeaderBar()
        self._left_header = left_header
        left_header.set_show_end_title_buttons(False)
        left_header.add_css_class("titlebar")
        left_header.add_css_class("tweak-titlebar-left")

        self.search_btn = Gtk.ToggleButton()  # Search Button
        self.search_btn.set_icon_name("edit-find-symbolic")
        self.search_btn.bind_property("active", self.searchbar, "search-mode-enabled",
                                      GObject.BindingFlags.BIDIRECTIONAL)
        self.search_btn.set_valign(Gtk.Align.CENTER)
        self.search_btn.add_css_class("image-button")
        left_header.pack_start(self.search_btn)

        lbl = Adw.WindowTitle.new(_("Tweaks"), "")  # Left label
        left_header.set_title_widget(lbl)

        self.builder = Gtk.Builder()
        assert(os.path.exists(gtweak.PKG_DATA_DIR))
        filename = os.path.join(gtweak.PKG_DATA_DIR, 'shell.ui')
        self.builder.add_from_file(filename)

        appmenu = self.builder.get_object('appmenu')  # Left AppMenu
        self.menu_btn.set_icon_name("open-menu-symbolic")
        self.menu_btn.set_menu_model(appmenu)
        left_header.pack_end(self.menu_btn)

        # Right Header
        right_header = Adw.HeaderBar(hexpand=True)
        self._right_header = right_header
        right_header.set_show_start_title_buttons(False)

        right_header.add_css_class("titlebar")
        right_header.add_css_class("tweak-titlebar-right")

        self._group_titlebar_widget = None

        self.title = Adw.WindowTitle.new("", "")
        right_header.set_title_widget(self.title)

        self.back_button = Gtk.Button.new_from_icon_name("go-previous-symbolic")
        self.back_button.connect("clicked", self._on_back_clicked)
        self.back_button.props.visible = header.props.folded
        right_header.pack_start(self.back_button)

        header.bind_property("folded", self.back_button, "visible",
                                        GObject.BindingFlags.SYNC_CREATE)
        header.bind_property("folded", right_header, "show-start-title-buttons")
        header.bind_property("folded", left_header, "show-end-title-buttons")

        lbl = Adw.WindowTitle.new(_("Tweaks"), "")
        left_header.set_title_widget(lbl)

        self.builder = Gtk.Builder()
        assert os.path.exists(gtweak.PKG_DATA_DIR)
        filename = os.path.join(gtweak.PKG_DATA_DIR, "shell.ui")
        self.builder.add_from_file(filename)

        header.append(left_header)
        header.get_page(left_header).set_name("sidebar")
        header.append(Gtk.Separator(orientation=Gtk.Orientation.VERTICAL))
        header.append(right_header)
        header.get_page(right_header).set_name("content")

        self.hsize_group.add_widget(left_header)

        return header

    def _setup_mainbox(self):
        # self.main_box.set_size_request(540, -1)

        # self.main_stack.add_css_class("background")
        self.main_stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)

        self.main_leaflet.bind_property("visible-child-name", self.header, "visible-child-name", GObject.BindingFlags.SYNC_CREATE)

    def _setup_sidebar(self):
        self.entry.placeholder_text=_("Search Tweaks…")
        if Gtk.check_version(3, 22, 20) is None:
            self.entry.set_input_hints(Gtk.InputHints.NO_EMOJI)
        self.entry.connect("search-changed", self._on_search)

        self.listbox.connect("row-selected", self._on_select_row)

        if not show_sound_tweaks:
            self.listbox.remove(self.list_box_row_sound)

    def _setup_sizegroups(self):
        start_pane_size_group = Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL)
        start_pane_size_group.add_widget(self.left_box)
        start_pane_size_group.add_widget(self._left_header)

        end_pane_size_group = Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL)
        end_pane_size_group.add_widget(self.right_box)
        end_pane_size_group.add_widget(self._right_header)

    def _setup_shortcut(self):
        s_trigger = Gtk.ShortcutTrigger.parse_string("<primary>f")
        s_action = Gtk.CallbackAction.new(lambda w, a, s: s.set_search_mode(True), self.searchbar)

        if s_trigger and s_action:
            shortcut = Gtk.Shortcut(trigger=s_trigger, action=s_action)
            self.add_shortcut(shortcut)

    def _load_css(self):
        if gtweak.defs.IS_DEVEL:
            self.add_css_class('devel')
        css_provider = Gtk.CssProvider()
        css_provider.load_from_path(
            os.path.join(gtweak.PKG_DATA_DIR, 'shell.css'))
        display = Gdk.Display.get_default()
        self.get_style_context().add_provider_for_display(display, css_provider,
                                            Gtk.STYLE_PROVIDER_PRIORITY_USER)

    @staticmethod
    def _list_filter_func(row, user_data: List[str]):
        name = row.props.tweakname
        if name in user_data:
            return row

    def _after_key_press(self, widget, event):
        if not self.search_btn.get_active() or not self.entry.is_focus():
            if self.entry.im_context_filter_keypress(event):
                self.search_btn.set_active(True)
                self.entry.grab_focus()

                # Text in entry is selected, deselect it
                l = self.entry.get_text_length()
                self.entry.select_region(l, l)
                return True

        return False

    def _on_list_changed(self, group):
        self.listbox.set_filter_func(self._list_filter_func, group)
        selected = self.listbox.get_selected_row()
        if not selected:
            return
        selected_tweakname = selected.props.tweakname
        if group and selected_tweakname not in group:
            index = sorted(self._model._tweak_group_names.keys()).index(group[0])
            row = self.listbox.get_row_at_index(index)
            self.listbox.select_row(row)
            self.entry.grab_focus()

    def _on_search(self, entry: Gtk.SearchEntry):
        txt = string_for_search(entry.get_text())
        group = self._model.search_matches(txt)
        self._on_list_changed(group)

    def _on_select_row(self, _, row: Gtk.ListBoxRow):
        if row:
            group = row.props.tweakname

            for tweak in tweaks:
              if tweak.name == group:

                self.main_stack.set_visible_child_name(tweak.name)
                self.title.set_title(tweak.title)
                self.main_leaflet.set_visible_child_name("content")

    def _on_find_toggled(self, _):
        self.searchbar.set_search_mode(not self.searchbar.get_search_mode())

    def _on_back_clicked(self, *_):
        # Clear the page selection when going back to allow
        # re-selecting it.
        self.listbox.unselect_all()

        self.main_leaflet.set_visible_child_name("sidebar")

    def show_only_tweaks(self, tweaks):
        for t in self._model.tweaks:
            if not isinstance(t, Gtk.Widget):
                continue
            if t in tweaks:
                t.show()
            else:
                t.hide()

