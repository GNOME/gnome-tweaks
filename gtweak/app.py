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

class ExtensionNotice(Gtk.MessageDialog):
    def __init__(self, modal, transient_for):
        Gtk.Dialog.__init__(self, modal=modal, transient_for=transient_for)

        self.add_button(_("_Continue"), Gtk.ResponseType.NONE)

        self.set_markup("<b>{0}</b>".format(_("Extensions Has Moved")))

        self.format_secondary_markup(
            "{0}\n\n{1}".format(
                # Translators: Placeholder will be replaced with "GNOME Extensions" in active link form
                _("Extensions management has been moved to {0}.").format(
                    '<a href="https://gitlab.gnome.org/GNOME/gnome-shell/-/blob/master/subprojects/extensions-app/README.md">GNOME Extensions</a>',
                ),
                # Translators: Placeholder will be replaced with "Flathub" in active link form
                _("We recommend downloading GNOME Extensions from {0} if your distribution does not include it.").format(
                    '<a href="https://flathub.org/apps/details/org.gnome.Extensions">Flathub</a>'
                )
            )
        )

class GnomeTweaks(Gtk.Application):

    def __init__(self):
        GLib.set_application_name(_("GNOME Tweaks"))
        Gtk.Application.__init__(self, application_id="org.gnome.tweaks")
        self.win = None

        self._settings = Gio.Settings.new('org.gnome.tweaks')

    def do_activate(self):
        if not self.win:
            model = TweakModel()
            self.win = Window(self, model)
            self.win.show_all()
        if not self.win.get_titlebar().props.folded:
            self.win.back_button.props.visible = False
        self.win.present()

        if self._settings.get_boolean('show-extensions-notice'):
            self.show_extensions_notice()
            self._settings.set_boolean('show-extensions-notice', False)

    def do_startup(self):
        Gtk.Application.do_startup(self)

        reset_action = Gio.SimpleAction.new("reset", None)
        reset_action.connect("activate", self.reset_cb)
        self.add_action(reset_action)

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

    def show_extensions_notice(self):
        extensionsdialog = ExtensionNotice(
            modal=True,
            transient_for=self.win
        )

        extensionsdialog.run()
        extensionsdialog.destroy()
