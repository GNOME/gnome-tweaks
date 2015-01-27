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
from __future__ import print_function

import os.path
import subprocess
import logging

from gi.repository import Gtk, Gdk, GLib, Gio

from gtweak.tweakmodel import Tweak
from gtweak.widgets import ListBoxTweakGroup, UI_BOX_SPACING
from gtweak.utils import AutostartManager, AutostartFile

def _list_header_func(row, before, user_data):
    if before and not row.get_header():
        row.set_header (Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL))

class _AppChooser(Gtk.Dialog):
    def __init__(self, main_window, running_exes):
        Gtk.Dialog.__init__(self, title=_("Applications"))

        self._running = {}
        self._all = {}

        self.entry = Gtk.SearchEntry(
                placeholder_text=_("Search Applications..."))
        self.entry.set_width_chars(30)

        self.searchbar = Gtk.SearchBar()
        self.searchbar.add(self.entry)
        self.searchbar.props.hexpand = True

        lb = Gtk.ListBox()
        lb.props.margin = 5
        lb.set_sort_func(self._sort_apps, None)
        lb.set_header_func(_list_header_func, None)
        lb.set_filter_func(self._list_filter_func, None)
        self.entry.connect("search-changed", lambda e: lb.invalidate_filter())

        apps = Gio.app_info_get_all()
        for a in apps:
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

        self.add_button(_("_Close"), Gtk.ResponseType.CLOSE)
        self.add_button(_("Add Application"), Gtk.ResponseType.OK)

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
            img = Gtk.Image.new_from_gicon(a.get_icon(),Gtk.IconSize.DIALOG)
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
      return False

    def _on_key_press(self, widget, event):
      keyname = Gdk.keyval_name(event.keyval)
      if keyname == 'Escape':
          if self.entry.is_focus():
              self.searchbar.set_search_mode(False)
              return True
          elif self.searchbar.get_search_mode():
              self.entry.grab_focus()
              return True
      elif keyname not in ['Escape', 'Up', 'Down']:
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
            img = Gtk.Image.new_from_gicon(icn,Gtk.IconSize.DIALOG)
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

class AutostartListBoxTweakGroup(ListBoxTweakGroup):
    def __init__(self):
        tweaks = []

        self.asm = AutostartManager()
        files = self.asm.get_user_autostart_files()
        for f in files:
            try:
                df = Gio.DesktopAppInfo.new_from_filename(f)
            except TypeError:
                logging.warning("Error loading desktopfile: %s" % f)
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

    def _on_remove_clicked(self, btn, widget, df):
        self.remove(widget)
        AutostartFile(df).update_start_at_login(False)

    def _on_add_clicked(self, btn):
        a = _AppChooser(
                self.main_window,
                set(self._get_running_executables()))
        a.show_all()
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
        for l in out.split('\n'):
            exe = l.split(' ')[0]
            if exe and exe[0] != '[': #kernel process
                exes.append( os.path.basename(exe) )

        return exes

TWEAK_GROUPS = [
    AutostartListBoxTweakGroup(),
]
