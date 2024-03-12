# Copyright (c) 2011 John Stowers
# SPDX-License-Identifier: GPL-3.0+
# License-Filename: LICENSES/GPL-3.0

import logging
import os.path
import subprocess
from typing import Set, Optional

from gi.repository import Adw, Gtk, Gdk, Gio, GObject, GLib

from gtweak.tweakmodel import Tweak, TweakGroup
from gtweak.utils import AutostartManager, AutostartFile


def _image_from_gicon(gicon):
    image = Gtk.Image.new_from_gicon(gicon)
    image.set_icon_size(Gtk.IconSize.LARGE)
    return image


class _AppChooserRow(Gtk.ListBoxRow):
    """The row in the appchooser to show desktop files """

    def __init__(self, app_info: Gio.AppInfo, is_running: bool, **kwargs):
        super().__init__(**kwargs)
        self.app_name = app_info.get_name().lower()
        self.is_running = is_running
        self.app_info = app_info

        vbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        vbox.set_margin_top(10)
        vbox.set_margin_bottom(10)
        vbox.set_margin_start(10)
        vbox.set_margin_end(10)

        icon = app_info.get_icon()
        if icon:
            img = _image_from_gicon(icon)
            img.set_hexpand(False)
        else:
            img = Gtk.Image.new_from_icon_name("application-x-executable")
            img.props.icon_size = Gtk.IconSize.LARGE
        app_name = app_info.get_name()
        lbl = Gtk.Label(label=app_name, hexpand=True,
                        halign=Gtk.Align.START, wrap=True)
        vbox.append(img)
        vbox.append(lbl)

        if is_running:
            lbl_running = Gtk.Label(label=_("running"))
            vbox.append(lbl_running)
        self.set_child(vbox)


class _AppChooser(Gtk.Dialog):
    """Presents a dialog to select a desktop file """

    def __init__(self, main_window, running_exes, startup_apps):
        uhb = Gtk.Settings.get_default().props.gtk_dialogs_use_header
        Gtk.Dialog.__init__(self, title=_("Select Application"), use_header_bar=uhb)

        self._running = {}
        self._all = {}

        # Build header bar buttons
        self.add_button(_("_Close"), Gtk.ResponseType.CANCEL)
        self.add_button(_("_Add"), Gtk.ResponseType.OK)
        self.set_default_response(Gtk.ResponseType.OK)

        self.entry = Gtk.SearchEntry(
            placeholder_text=_("Search Applications…"))
        self.entry.set_width_chars(30)
        self.entry.props.activates_default = True
        self.entry.connect("search-changed", self._on_search_entry_changed)

        self.searchbar = Gtk.SearchBar()
        self.searchbar.set_child(self.entry)
        self.searchbar.set_hexpand(True)
        self.searchbar.set_key_capture_widget(self)

        lb = Gtk.ListBox()
        lb.set_activate_on_single_click(False)
        lb.set_sort_func(self._list_sort_func, None)
        lb.set_filter_func(self._list_filter_func, self.entry)
        lb.connect("row-activated",
                   lambda b, r: self.response(Gtk.ResponseType.OK) if r.get_mapped() else None)
        lb.connect("row-selected", self._on_row_selected)

        apps = filter(lambda _app: _app.should_show() and _app.get_id() not in startup_apps,
                      Gio.app_info_get_all())

        for app in apps:
            running = app.get_executable() in running_exes
            if not app.get_name():
                continue
            w = _AppChooserRow(app, running)
            if w:
                lb.append(w)

        sw = Gtk.ScrolledWindow(vexpand=True, margin_top=2, margin_bottom=2,
                                margin_start=2, margin_end=2)
        sw.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        sw.set_child(lb)

        header_bar = self.get_header_bar()
        if header_bar:
            searchbtn = Gtk.ToggleButton(valign=Gtk.Align.CENTER)
            searchbtn.set_icon_name("edit-find-symbolic")
            header_bar.pack_end(searchbtn)
            self._binding = searchbtn.bind_property(
                "active", self.searchbar,
                "search-mode-enabled", GObject.BindingFlags.BIDIRECTIONAL)

        self.get_content_area().append(self.searchbar)
        self.get_content_area().append(sw)
        self.set_modal(True)
        self.set_transient_for(main_window)
        self.set_size_request(320, 300)

        self.listbox = lb
        self._setup_shortcut()

    def _setup_shortcut(self):
        s_trigger = Gtk.ShortcutTrigger.parse_string("<primary>f")
        s_action = Gtk.CallbackAction.new(lambda w, a, s: s.set_search_mode(True), self.searchbar)

        if s_trigger and s_action:
            shortcut = Gtk.Shortcut(trigger=s_trigger, action=s_action)
            self.add_shortcut(shortcut)

    @staticmethod
    def _list_sort_func(row_a: _AppChooserRow, row_b: _AppChooserRow, _):
        a_isrunning = row_a.is_running
        b_isrunning = row_b.is_running

        if a_isrunning and not b_isrunning:
            return -1
        elif not a_isrunning and b_isrunning:
            return 1
        else:
            aname = row_a.app_name
            bname = row_b.app_name

            if aname < bname:
                return -1
            elif aname > bname:
                return 1
            else:
                return 0

    @staticmethod
    def _list_filter_func(row: _AppChooserRow, entry: Gtk.SearchEntry) -> bool:
        txt = entry.get_text().lower()
        if txt in row.app_name:
            return True
        return False

    def _on_search_entry_changed(self, editable):
        self.listbox.invalidate_filter()
        selected = self.listbox.get_selected_row()
        if selected and selected.get_mapped():
            self.set_response_sensitive(Gtk.ResponseType.OK, True)
        else:
            self.set_response_sensitive(Gtk.ResponseType.OK, False)

    def _on_row_selected(self, box, row):
        if row and row.get_mapped():
            self.set_response_sensitive(Gtk.ResponseType.OK, True)
        else:
            self.set_response_sensitive(Gtk.ResponseType.OK, False)

    def get_selected_appinfo(self) -> Optional[Gio.AppInfo]:
        row: _AppChooserRow = self.listbox.get_selected_row()

        if row is not None:
            return row.app_info
        return None


class _StartupAppRowTweak(Adw.ActionRow, Tweak):

    def __init__(self, desktop_info: Gio.AppInfo, **options):
        Adw.PreferencesRow.__init__(self)
        Tweak.__init__(self, desktop_info.get_name(), desktop_info.get_description(), **options)

        icon = desktop_info.get_icon()
        if icon:
            app_icon = _image_from_gicon(icon)
        else:
            app_icon = Gtk.Image.new_from_icon_name("image-missing")
            app_icon.set_icon_size(Gtk.IconSize.LARGE)

        self.btn = Gtk.Button(icon_name="edit-delete-symbolic")
        self.btn.set_tooltip_text(_("Remove"))

        self.btn.add_css_class("flat")
        self.btn.set_vexpand(False)
        self.btn.set_valign(Gtk.Align.CENTER)

        self.set_title(desktop_info.get_name())
        self.add_prefix(app_icon)
        self.add_suffix(self.btn)
        self.app_info = desktop_info

        controller_key = Gtk.EventControllerKey()
        self.add_controller(controller_key)
        controller_key.connect("key-pressed", self._on_key_press_event)

    def _on_key_press_event(self, _, keyval: int, _1, _2):
        if keyval in [Gdk.KEY_Delete, Gdk.KEY_KP_Delete, Gdk.KEY_BackSpace]:
            self.btn.activate()
            return True
        return False


class AutostartTweakGroup(Adw.PreferencesPage, TweakGroup):

    def __init__(self, *tweaks, **options):
        name: str = _("Startup Applications")
        desc: str = _("Startup applications are automatically started when you log in.")
        Adw.PreferencesPage.__init__(self)
        TweakGroup.__init__(self, "startup-applications", name, **options)

        self.tweaks = [Tweak(name, desc, **options)]

        pregroup = Adw.PreferencesGroup()
        # Preferencee Group Header
        pregroup.set_title(name)
        pregroup.set_description(desc)

        self.btn_add_startup = Gtk.Button(valign=Gtk.Align.CENTER)
        self.btn_add_startup.set_icon_name("list-add-symbolic")
        self.btn_add_startup.add_css_class("flat")
        pregroup.set_header_suffix(self.btn_add_startup)

        # Body
        self.stack = Gtk.Stack()
        self.status_page = Adw.StatusPage()
        self.pg_startup_apps = Adw.PreferencesGroup()
        self._setup_stack_view()

        self._startup_dapps = self._get_startup_desktop_files()
        self._setup_startup_app_row()

        self.__init_connections()
        pregroup.add(self.stack)
        self.add(pregroup)
        self._set_visible_page()

    def _setup_stack_view(self):
        self.stack.set_vexpand(True)
        self.stack.set_hhomogeneous(True)
        self.stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)

        # Empty Page
        self.status_page.set_icon_name("application-x-executable-symbolic")
        self.status_page.set_title(_("No Startup Applications"))
        self.status_page.set_description(_("Add a startup application"))
        self.status_page.add_css_class("dim-label")

        self.stack.add_child(self.status_page)
        self.stack.add_child(self.pg_startup_apps)

    def _setup_startup_app_row(self):
        """ Add a row for each autostart applications existing"""

        dfiles = self._startup_dapps
        for dfile in dfiles:
            app_row = _StartupAppRowTweak(dfile)
            app_row.btn.connect("clicked", self._on_remove_clicked, app_row)
            self.pg_startup_apps.add(app_row)
            self.tweaks.append(app_row)

    def _set_visible_page(self):
        if len(self._startup_dapps) > 0:
            self.stack.set_visible_child(self.pg_startup_apps)
        else:
            self.stack.set_visible_child(self.status_page)

    def _on_add_clicked(self, _: Gtk.Button):
        def _on_response_appchooser(chooser: _AppChooser, response_id: int):
            if response_id == Gtk.ResponseType.OK:
                appinfo = chooser.get_selected_appinfo()

                if appinfo:
                    AutostartFile(appinfo).update_start_at_login(True)
                    arow_app_row = _StartupAppRowTweak(appinfo)
                    arow_app_row.btn.connect("clicked", self._on_remove_clicked, arow_app_row)

                    self.pg_startup_apps.add(arow_app_row)
                    self._startup_dapps.add(appinfo)
                    self._set_visible_page()
            chooser.destroy()

        startup_app_ids = tuple(map(lambda x: x.get_id(), self._startup_dapps))

        Gio.Application.get_default().mark_busy()
        a = _AppChooser(self.main_window, self._get_running_executables(), startup_app_ids)
        a.connect("response", _on_response_appchooser)
        Gio.Application.get_default().unmark_busy()
        a.present()

    def _on_remove_clicked(self, btn, app_row: _StartupAppRowTweak):
        app_info = app_row.app_info
        AutostartFile(app_info).update_start_at_login(False)

        self.pg_startup_apps.remove(app_row)
        self._startup_dapps.remove(app_info)
        self._set_visible_page()

    def __init_connections(self):
        self.btn_add_startup.connect("clicked", self._on_add_clicked)

    @staticmethod
    def _get_startup_desktop_files():
        asm = AutostartManager()
        autostart_files = asm.get_user_autostart_files()
        dfiles = set()

        for file in autostart_files:
            try:
                dappinfo = Gio.DesktopAppInfo.new_from_filename(file)
            except TypeError:
                logging.warning(f"Error loading desktop file: {file}")
            else:
                if not AutostartFile(dappinfo).is_start_at_login_enabled():
                    continue
                dfiles.add(dappinfo)

        return dfiles

    @staticmethod
    def _get_running_executables() -> Set[str]:
        exes = set()
        cmd = subprocess.Popen([
            'ps', '-e', '-w', '-w', '-U',
            str(os.getuid()), '-o', 'cmd'],
            stdout=subprocess.PIPE)
        out = cmd.communicate()[0]
        for process in out.decode('utf8').split('\n'):
            exe = process.split(' ')[0]
            if exe and exe[0] != '[':  # kernel process
                exes.add(os.path.basename(exe))

        return exes

TWEAK_GROUP = AutostartTweakGroup()
