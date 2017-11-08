# Copyright (c) 2011 John Stowers
# SPDX-License-Identifier: GPL-3.0+
# License-Filename: LICENSES/GPL-3.0

import os.path
import subprocess
import logging

from gi.repository import Gtk, Gdk, GLib, Gio, GObject

from gtweak.tweakmodel import Tweak
from gtweak.widgets import ListBoxTweakGroup, UI_BOX_SPACING
from gtweak.utils import AutostartManager, AutostartFile

def _image_from_gicon(gicon):
    image = Gtk.Image.new_from_gicon(gicon, Gtk.IconSize.DIALOG)
    (_, _, h) = Gtk.IconSize.lookup(Gtk.IconSize.DIALOG)
    image.set_pixel_size(h)
    return image

def _list_header_func(row, before, user_data):
    if before and not row.get_header():
        row.set_header (Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL))


class AutostartTitle(Gtk.Box, Tweak):

    def __init__(self, **options):
        Gtk.Box.__init__(self)
        desc = _("Startup applications are automatically started when you log in.")
        Tweak.__init__(self, _("Startup Applications"), desc, **options)

        label = Gtk.Label(desc)
        label.get_style_context().add_class("dim-label")
        self.props.margin_bottom = 10
        self.add(label)


class _AppChooser(Gtk.Dialog):
    def __init__(self, main_window, running_exes, startup_apps):
        uhb = Gtk.Settings.get_default().props.gtk_dialogs_use_header
        Gtk.Dialog.__init__(self, title=_("Applications"), use_header_bar=uhb)

        self._running = {}
        self._all = {}

        self.entry = Gtk.SearchEntry(
                placeholder_text=_("Search Applications…"))
        self.entry.set_width_chars(30)
        self.entry.props.activates_default=True
        if (Gtk.check_version(3, 22, 20) == None):
            self.entry.set_input_hints(Gtk.InputHints.NO_EMOJI)

        self.searchbar = Gtk.SearchBar()
        self.searchbar.add(self.entry)
        self.searchbar.props.hexpand = True
        # Translators: This is the accelerator for opening the AppChooser search-bar
        self._search_key, self._search_mods = Gtk.accelerator_parse(_("<primary>f"))

        lb = Gtk.ListBox()
        lb.props.margin = 5
        lb.props.activate_on_single_click = False
        lb.set_sort_func(self._sort_apps, None)
        lb.set_header_func(_list_header_func, None)
        lb.set_filter_func(self._list_filter_func, None)
        self.entry.connect("search-changed", self._on_search_entry_changed)
        lb.connect("row-activated", lambda b, r: self.response(Gtk.ResponseType.OK) if r.get_mapped() else None)
        lb.connect("row-selected", self._on_row_selected)

        apps = Gio.app_info_get_all()
        for a in apps:
            if a.get_id() not in startup_apps:
                if a.should_show():
                    running = a.get_executable() in running_exes
                    w = self._build_widget(
                        a,
                        _("running") if running else "")
                    if w:
                        self._all[w] = a
                        self._running[w] = running
                        lb.add(w)

        sw = Gtk.ScrolledWindow()
        sw.props.hscrollbar_policy = Gtk.PolicyType.NEVER
        sw.add(lb)

        self.add_button(_("_Close"), Gtk.ResponseType.CANCEL)
        self.add_button(_("_Add"), Gtk.ResponseType.OK)
        self.set_default_response(Gtk.ResponseType.OK)

        if self.props.use_header_bar:
            searchbtn = Gtk.ToggleButton()
            searchbtn.props.valign = Gtk.Align.CENTER
            image = Gtk.Image(icon_name = "edit-find-symbolic", icon_size = Gtk.IconSize.MENU)
            searchbtn.add(image)
            context = searchbtn.get_style_context()
            context.add_class("image-button")
            context.remove_class("text-button")
            self.get_header_bar().pack_end(searchbtn)
            self._binding = searchbtn.bind_property("active", self.searchbar, "search-mode-enabled", GObject.BindingFlags.BIDIRECTIONAL)

        self.get_content_area().pack_start(self.searchbar, False, False, 0)
        self.get_content_area().pack_start(sw, True, True, 0)
        self.set_modal(True)
        self.set_transient_for(main_window)
        self.set_size_request(400,300)

        self.listbox = lb

        self.connect("key-press-event", self._on_key_press)

    def _sort_apps(self, a, b, user_data):
        arun = self._running.get(a)
        brun = self._running.get(b)

        if arun and not brun:
            return -1
        elif not arun and brun:
            return 1
        else:
            aname = self._all.get(a).get_name()
            bname = self._all.get(b).get_name()

            if aname < bname:
                return -1
            elif aname > bname:
                return 1
            else:
                return 0

    def _build_widget(self, a, extra):
        row = Gtk.ListBoxRow()
        g = Gtk.Grid()
        if not a.get_name():
            return None
        icn = a.get_icon()
        if icn:
            img = _image_from_gicon(icn)
            g.attach(img, 0, 0, 1, 1)
            img.props.hexpand = False
        else:
             img = None #attach_next_to treats this correctly
        lbl = Gtk.Label(label=a.get_name(), xalign=0)
        g.attach_next_to(lbl,img,Gtk.PositionType.RIGHT,1,1)
        lbl.props.hexpand = True
        lbl.props.halign = Gtk.Align.START
        lbl.props.vexpand = False
        lbl.props.valign = Gtk.Align.CENTER
        if extra:
            g.attach_next_to(
                Gtk.Label(label=extra),
                lbl,Gtk.PositionType.RIGHT,1,1)
        row.add(g)
        #row.get_style_context().add_class('tweak-white')
        return row

    def _list_filter_func(self, row, unused):
      txt = self.entry.get_text().lower()
      grid = row.get_child()
      for sib in grid.get_children():
          if type(sib) == Gtk.Label:
              if txt in sib.get_text().lower():
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

    def _on_key_press(self, widget, event):
      mods = event.state & Gtk.accelerator_get_default_mod_mask()
      if event.keyval == self._search_key and mods == self._search_mods:
          self.searchbar.set_search_mode(not self.searchbar.get_search_mode())
          return True
      keyname = Gdk.keyval_name(event.keyval)
      if keyname == 'Escape':
          if self.searchbar.get_search_mode():
              self.searchbar.set_search_mode(False)
              return True
      elif keyname not in ['Up', 'Down']:
          if not self.entry.is_focus() and self.searchbar.get_search_mode():
              if self.entry.im_context_filter_keypress(event):
                  self.entry.grab_focus()
                  l = self.entry.get_text_length()
                  self.entry.select_region(l, l)
                  return True

          return self.searchbar.handle_event(event)

      return False

    def get_selected_app(self):
        row = self.listbox.get_selected_row()
        if row:
            return self._all.get(row)
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

        self.add(grid)

        self.props.margin_start = 1
        self.props.margin_end = 1
        self.get_style_context().add_class('tweak-startup')

        self.btn = btn
        self.app_id = df.get_id()
        self.connect("key-press-event", self._on_key_press_event)

    def _on_key_press_event(self, row, event):
        if event.keyval in [Gdk.KEY_Delete, Gdk.KEY_KP_Delete, Gdk.KEY_BackSpace]:
            self.btn.activate()
            return True
        return False

class AddStartupTweak(Gtk.ListBoxRow, Tweak):
    def __init__(self, **options):
        Gtk.ListBoxRow.__init__(self)
        Tweak.__init__(self, _("New startup application"),
                       _("Add a new application to be run at startup"),
                       **options)

        img = Gtk.Image()
        img.set_from_icon_name("list-add-symbolic", Gtk.IconSize.BUTTON)
        self.btn = Gtk.Button(label="", image=img, always_show_image=True)
        self.btn.get_style_context().remove_class("button")
        self.add(self.btn)
        self.get_style_context().add_class('tweak-startup')
        self.connect("map", self._on_map)
        self.connect("unmap", self._on_unmap)

    def _on_map(self, row):
        toplevel=self.get_toplevel()
        if toplevel.is_toplevel:
            for k in [Gdk.KEY_equal, Gdk.KEY_plus, Gdk.KEY_KP_Add]:
                toplevel.add_mnemonic(k, self.btn)

    def _on_unmap(self, row):
        toplevel=self.get_toplevel()
        if toplevel.is_toplevel:
            for k in [Gdk.KEY_equal, Gdk.KEY_plus, Gdk.KEY_KP_Add]:
                toplevel.remove_mnemonic(k, self.btn)

class AutostartListBoxTweakGroup(ListBoxTweakGroup):
    def __init__(self):
        tweaks = [AutostartTitle()]

        self.asm = AutostartManager()
        files = self.asm.get_user_autostart_files()
        for f in files:
            try:
                df = Gio.DesktopAppInfo.new_from_filename(f)
            except TypeError:
                logging.warning("Error loading desktopfile: %s" % f)
                continue

            if not AutostartFile(df).is_start_at_login_enabled():
                continue

            sdf = _StartupTweak(df)
            sdf.btn.connect("clicked", self._on_remove_clicked, sdf, df)
            tweaks.append( sdf )

        add = AddStartupTweak()
        add.btn.connect("clicked", self._on_add_clicked)
        tweaks.append(add)

        ListBoxTweakGroup.__init__(self,
            _("Startup Applications"),
            *tweaks,
            css_class='tweak-group-startup')
        self.set_header_func(_list_header_func, None)
        self.connect("row-activated", lambda b, row: add.btn.activate() if row == add else None)

    def _on_remove_clicked(self, btn, widget, df):
        self.remove(widget)
        AutostartFile(df).update_start_at_login(False)

    def _on_add_clicked(self, btn):
        Gio.Application.get_default().mark_busy()
        startup_apps = set()
        self.foreach(lambda row: startup_apps.add(row.app_id) if type(row) is _StartupTweak else None)
        a = _AppChooser(
                self.main_window,
                set(self._get_running_executables()),
                startup_apps)
        a.show_all()
        Gio.Application.get_default().unmark_busy()
        resp = a.run()
        if resp == Gtk.ResponseType.OK:
            df = a.get_selected_app()
            if df:
                AutostartFile(df).update_start_at_login(True)
                sdf = _StartupTweak(df)
                sdf.btn.connect("clicked", self._on_remove_clicked, sdf, df)
                self.add_tweak_row(sdf, 0).show_all()
        a.destroy()

    def _get_running_executables(self):
        exes = []
        cmd = subprocess.Popen([
                    'ps','-e','-w','-w','-U',
                    str(os.getuid()),'-o','cmd'],
                    stdout=subprocess.PIPE)
        out = cmd.communicate()[0]
        for l in out.decode('utf8').split('\n'):
            exe = l.split(' ')[0]
            if exe and exe[0] != '[': #kernel process
                exes.append( os.path.basename(exe) )

        return exes

TWEAK_GROUPS = [
    AutostartListBoxTweakGroup(),
]
