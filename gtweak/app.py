# Copyright (c) 2011 John Stowers
# SPDX-License-Identifier: GPL-3.0+
# License-Filename: LICENSES/GPL-3.0

import os.path

from gi.repository import Gtk
from gi.repository import Gio
from gi.repository import GLib

import gtweak
from gtweak.defs import VERSION
from gtweak.tweakmodel import TweakModel
from gtweak.tweakview import Window
from gtweak.utils import SchemaList
from gtweak.gshellwrapper import GnomeShellFactory
from gtweak.utils import DisableExtension


class GnomeTweaks(Gtk.Application):

    def __init__(self):
        GLib.set_application_name(_("GNOME Tweaks"))
        Gtk.Application.__init__(self, application_id="org.gnome.tweaks")
        self.win = None

    def do_activate(self):
        if not self.win:
            model = TweakModel()
            self.win = Window(self, model)
            self.win.show_all()
            self.win.back_button.props.visible = False
        self.win.present()

    def do_startup(self):
        Gtk.Application.do_startup(self)

        reset_action = Gio.SimpleAction.new("reset", None)
        reset_action.connect("activate", self.reset_cb)
        self.add_action(reset_action)

        disable_extension_action = Gio.SimpleAction.new("disable_extension", None)
        disable_extension_action.connect("activate", self.disable_cb)
        self.add_action(disable_extension_action)

        help_action = Gio.SimpleAction.new("help", None)
        help_action.connect("activate", self.help_cb)
        self.add_action(help_action)

        about_action = Gio.SimpleAction.new("about", None)
        about_action.connect("activate", self.about_cb)
        self.add_action(about_action)

    def reset_cb(self, action, parameter):
        dialog = Gtk.MessageDialog(self.win, 0, Gtk.MessageType.QUESTION,
                                   Gtk.ButtonsType.OK_CANCEL, _("Reset to Defaults"))
        dialog.format_secondary_text(_("Reset all tweak settings to the original default state?"))
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            s = SchemaList()
            s.reset()
        dialog.destroy()

    def help_cb(self, action, parameter):
        print("This does nothing. It is only a demonstration.")

    def disable_cb(self, action, parameter):
        ds = DisableExtension()
        ds.disable()

    def about_cb(self, action, parameter):
        aboutdialog = Gtk.AboutDialog(modal=True, transient_for=self.win)
        aboutdialog.set_program_name(aboutdialog.get_program_name() + " %s" % VERSION)

        _shell = GnomeShellFactory().get_shell()
        if _shell is not None:
            if _shell.mode == "user":
                about_comment = _("GNOME Shell") + " %s" % _shell.version
            else:
                about_comment = (_("GNOME Shell") + " %s " + _("(%s mode)")) % \
                    (_shell.version, _shell.mode)
        else:
            about_comment = _("GNOME Shell is not running")

        about_comment += "\n" + _("GTK") + " %d.%d.%d" % \
            (Gtk.get_major_version(), Gtk.get_minor_version(), Gtk.get_micro_version())
        aboutdialog.set_comments(about_comment)

        aboutdialog.set_copyright("Copyright © 2011 - 2013 John Stowers.")
        aboutdialog.set_logo_icon_name("org.gnome.tweaks")
        aboutdialog.set_website("https://wiki.gnome.org/Apps/Tweaks")
        aboutdialog.set_website_label(_("Homepage"))
        aboutdialog.set_license_type(Gtk.License.GPL_3_0)

        AUTHORS = [
                "John Stowers <john.stowers@gmail.com>"
                ]

        aboutdialog.set_authors(AUTHORS)
        aboutdialog.connect("response", lambda w, r: aboutdialog.destroy())
        aboutdialog.show()

    def quit_cb(self, action, parameter):
        self.quit()
