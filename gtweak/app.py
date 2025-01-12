# Copyright (c) 2011 John Stowers
# SPDX-License-Identifier: GPL-3.0+
# License-Filename: LICENSES/GPL-3.0

from gi.repository import Adw
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

        self.props.secondary_use_markup = True
        self.props.secondary_text = "{0}\n\n{1}".format(
            # Translators: Placeholder will be replaced with "GNOME Extensions" in active link form
            _("Extensions management has been moved to {0}.").format(
                '<a href="https://gitlab.gnome.org/GNOME/gnome-shell/-/blob/HEAD/subprojects/extensions-app/README.md">GNOME Extensions</a>',
            ),
            # Translators: Placeholder will be replaced with "Flathub" in active link form
            _("We recommend downloading GNOME Extensions from {0} if your distribution does not include it.").format(
                '<a href="https://flathub.org/apps/details/org.gnome.Extensions">Flathub</a>'
            )
        )

_application = None

def get_application():
    return _application

def get_window():
    return _application.win

class GnomeTweaks(Adw.Application):

    def __init__(self):
        global _application

        _application = self

        GLib.set_application_name(_("GNOME Tweaks"))
        super().__init__(application_id=gtweak.APP_ID)
        self.win = None

        self._settings = Gio.Settings.new('org.gnome.tweaks')

    def do_activate(self):
        if not self.win:
            model = TweakModel()
            self.win = Window(self, model)
        self.win.present()

        if self._settings.get_boolean('show-extensions-notice'):
            self.show_extensions_notice()
            self._settings.set_boolean('show-extensions-notice', False)

    def do_startup(self):
        Adw.Application.do_startup(self)

        self.set_accels_for_action("window.close", ["<primary>w"])
        self._create_action("quit", self.quit_app, ["<primary>q"])
        self._create_action("about", self.about_cb)
        self._create_action("reset", self.reset_cb)

    def quit_app(self, *_):
        self.quit()

    def reset_cb(self, action, parameter):
        def _on_dialog_response(_dialog, response_type):
            if response_type == Gtk.ResponseType.OK:
                SchemaList.reset()

            _dialog.destroy()

        dialog = Gtk.MessageDialog(transient_for=self.win,
                                   modal=True,
                                   message_type=Gtk.MessageType.QUESTION,
                                   buttons=Gtk.ButtonsType.OK_CANCEL,
                                   text=_("Reset to Defaults"),
                                   secondary_text=_("Reset all tweaks settings to the original default state?"))

        dialog.connect("response", _on_dialog_response)
        dialog.present()

    def about_cb(self, action, parameter):
        _shell = GnomeShellFactory().get_shell()
        if _shell is not None:
            if _shell.mode == "user":
                about_comment = f'{_("GNOME Shell")} {_shell.version}'

            else:
                about_comment = (_("GNOME Shell") + " %s " + _("(%s mode)")) % \
                    (_shell.version, _shell.mode)
        else:
            about_comment = _("GNOME Shell is not running")

        about_comment += f'\n{_("GTK")} {Gtk.get_major_version()}.{Gtk.get_minor_version()}.{Gtk.get_micro_version()}'

        AUTHORS = [
                "John Stowers <john.stowers@gmail.com>"
                ]

        aboutdialog = Adw.AboutWindow(
            application_name=GLib.get_application_name(),
            application_icon=gtweak.APP_ID,
            comments=about_comment,
            copyright="Copyright © 2011 - 2013 John Stowers.",
            developer_name="John Stowers",
            # TRANSLATORS: Add your name/nickname here (one name per line),
            # they will be displayed in the "about" dialog
            translator_credits=_("translator-credits"),
            developers=AUTHORS,
            transient_for=self.win,
            version=VERSION,
            website="https://wiki.gnome.org/Apps/Tweaks",
            issue_url="https://gitlab.gnome.org/GNOME/gnome-tweaks/-/issues",
            license_type=Gtk.License.GPL_3_0
        )

        aboutdialog.present()

    def show_extensions_notice(self):
        extensionsdialog = ExtensionNotice(
            modal=True,
            transient_for=self.win
        )

        extensionsdialog.connect("response", lambda _dialog, _: _dialog.destroy())
        extensionsdialog.show()

    def _create_action(self, name, callback, shortcuts=None):
        """Add an application action.

        :param name: the name of the action
        :param callback: the function to be called when the action is activated
        :param shortcuts:
        :return: an optional list of accelerators
        """
        action = Gio.SimpleAction.new(name, None)
        action.connect("activate", callback)
        self.add_action(action)
        if shortcuts:
            self.set_accels_for_action(f"app.{name}", shortcuts)
