# Copyright (c) 2011 John Stowers
# SPDX-License-Identifier: GPL-3.0+
# License-Filename: LICENSES/GPL-3.0

import os.path
import subprocess
import logging
from typing import Set, Optional

from gi.repository import Gtk, Gdk, Gio, GObject

from gtweak.tweakmodel import Tweak
from gtweak.widgets import ListBoxTweakGroup
from gtweak.utils import AutostartManager, AutostartFile


def _image_from_gicon(gicon):
    image = Gtk.Image.new_from_gicon(gicon)
    image.set_icon_size(Gtk.IconSize.LARGE)
    return image


class AutostartTitle(Gtk.Box, Tweak):

    def __init__(self, **options):
        Gtk.Box.__init__(self)
        desc = _("Startup applications are automatically started when you log in.")
        Tweak.__init__(self, _("Startup Applications"), desc, **options)

        label = Gtk.Label(label=desc, margin_start=12, margin_top=12)
        label.set_wrap(True)
        label.add_css_class("dim-label")
        self.set_margin_bottom(10)
        self.append(label)


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
        Gtk.Dialog.__init__(self, title=_("Applications"), use_header_bar=uhb)

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
        lb.connect("row-activated", lambda b, r: self.response(Gtk.ResponseType.OK) if r.get_mapped() else None)
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
                                margin_start=2,margin_end=2)
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
        self.set_size_request(300, 300)

        self.listbox = lb
        self._setup_shortcut()

    def _setup_shortcut(self):
        # Translators: This is the accelerator for opening the AppChooser search-bar
        s_trigger = Gtk.ShortcutTrigger.parse_string(_("<primary>f"))
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


class _StartupTweak(Gtk.ListBoxRow, Tweak):
    def __init__(self, df, **options):
        Gtk.ListBoxRow.__init__(self)
        Tweak.__init__(self,
                        df.get_name(),
                        df.get_description(),
                        **options)

        grid = Gtk.Grid(column_spacing=10)

        icn = df.get_icon()
        if icn:
            img = _image_from_gicon(icn)
            grid.attach(img, 0, 0, 1, 1)
        else:
            img = None #attach_next_to treats this correctly

        lbl = Gtk.Label(label=df.get_name(), xalign=0.0)
        grid.attach_next_to(lbl,img,Gtk.PositionType.RIGHT,1,1)
        lbl.props.hexpand = True
        lbl.props.halign = Gtk.Align.START

        btn = Gtk.Button(label=_("Remove"))
        grid.attach_next_to(btn,lbl,Gtk.PositionType.RIGHT,1,1)
        btn.props.vexpand = False
        btn.props.valign = Gtk.Align.CENTER

        self.set_child(grid)

        self.set_margin_start(1)
        self.set_margin_end(1)
        self.add_css_class('tweak-startup')

        self.btn = btn
        self.app_id = df.get_id()

        controller_key = Gtk.EventControllerKey()
        self.add_controller(controller_key)
        controller_key.connect("key-pressed", self._on_key_press_event)

    def _on_key_press_event(self, _, keyval: int, _1, _2):
        if keyval in [Gdk.KEY_Delete, Gdk.KEY_KP_Delete, Gdk.KEY_BackSpace]:
            self.btn.activate()
            return True
        return False


class AddStartupTweak(Gtk.ListBoxRow, Tweak):
    def __init__(self, **options):
        Gtk.ListBoxRow.__init__(self)
        Tweak.__init__(self, _("New startup application"),
                       _("Add a new application to be run at startup"),
                       **options)

        self.btn = Gtk.Button.new_from_icon_name("list-add-symbolic")
        self.btn.get_style_context().remove_class("button")
        self.set_child(self.btn)
        self.add_css_class('tweak-startup')


class AutostartListBoxTweakGroup(ListBoxTweakGroup):
    def __init__(self):
        tweaks = [AutostartTitle()]

        self.asm = AutostartManager()
        files = self.asm.get_user_autostart_files()
        self._startup_apps_id = set()
        for f in files:
            try:
                df = Gio.DesktopAppInfo.new_from_filename(f)
            except TypeError:
                logging.warning("Error loading desktopfile: %s" % f)
                continue

            if not AutostartFile(df).is_start_at_login_enabled():
                continue

            sdf = _StartupTweak(df)
            self._startup_apps_id.add(df.get_id())
            sdf.btn.connect("clicked", self._on_remove_clicked, sdf, df)
            tweaks.append(sdf)

        add = AddStartupTweak()
        add.btn.connect("clicked", self._on_add_clicked)
        tweaks.append(add)

        ListBoxTweakGroup.__init__(self,
            "startup-applications",
            _("Startup Applications"),
            *tweaks,
            css_class='tweak-group-startup')

        self.add_css_class("boxed-list")
        self.connect("row-activated", lambda b, row: add.btn.activate() if row == add else None)

    def _on_remove_clicked(self, btn, widget, df):
        self.remove(widget)
        self._startup_apps_id.remove(df.get_id())
        AutostartFile(df).update_start_at_login(False)

    def _on_add_clicked(self, btn):
        def _on_response_appchooser(chooser: _AppChooser, response_id: int):
            if response_id == Gtk.ResponseType.OK:
                appinfo = chooser.get_selected_appinfo()
                if appinfo:
                    AutostartFile(appinfo).update_start_at_login(True)
                    sdf = _StartupTweak(appinfo)
                    # Hide the new startup tweak from the dialog list
                    # TODO: Update the list based on the source file list
                    self._startup_apps_id.add(appinfo.get_id())
                    sdf.btn.connect("clicked", self._on_remove_clicked, sdf, appinfo)
                    self.add_tweak_row(sdf, False, 1).show()
            chooser.destroy()

        Gio.Application.get_default().mark_busy()
        a = _AppChooser(
                self.main_window,
                self._get_running_executables(),
                self._startup_apps_id)
        a.connect("response", _on_response_appchooser)
        Gio.Application.get_default().unmark_busy()
        a.present()

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

TWEAK_GROUP = AutostartListBoxTweakGroup()
