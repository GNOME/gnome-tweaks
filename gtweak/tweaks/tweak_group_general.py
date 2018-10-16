# Copyright (c) 2011 John Stowers
# SPDX-License-Identifier: GPL-3.0+
# License-Filename: LICENSES/GPL-3.0

from gi.repository import Gio, GLib, Gtk

import gtweak
from gtweak.gshellwrapper import GnomeShellFactory
from gtweak.tweakmodel import Tweak
from gtweak.widgets import ListBoxTweakGroup, GetterSetterSwitchTweak, GSettingsSwitchTweak
from gtweak.utils import AutostartFile

_shell = GnomeShellFactory().get_shell()
_shell_not_ubuntu = True

if _shell:
  _shell_not_ubuntu = _shell.mode != 'ubuntu'

class IgnoreLidSwitchTweak(GetterSetterSwitchTweak):
    def __init__(self, **options):
        self._inhibitor_name = "gnome-tweak-tool-lid-inhibitor"
        self._inhibitor_path = "%s/%s" % (gtweak.LIBEXEC_DIR, self._inhibitor_name)

        self._dfile = AutostartFile(None,
                                    autostart_desktop_filename = "ignore-lid-switch-tweak.desktop",
                                    exec_cmd = self._inhibitor_path)

        GetterSetterSwitchTweak.__init__(self, _("Suspend when laptop lid is closed"), **options)

    def get_active(self):
        return not self._sync_inhibitor()

    def set_active(self, v):
        self._dfile.update_start_at_login(not v)
        self._sync_inhibitor()

    def _sync_inhibitor(self):
        if (self._dfile.is_start_at_login_enabled()):
            GLib.spawn_command_line_async(self._inhibitor_path)
            return True
        else:
            bus = Gio.bus_get_sync(Gio.BusType.SESSION, None)
            bus.call('org.gnome.tweak-tool.lid-inhibitor',
                     '/org/gnome/tweak_tool/lid_inhibitor',
                     'org.gtk.Actions',
                     'Activate',
                     GLib.Variant('(sava{sv})', ('quit', [], {})),
                     None, 0, -1, None)
            return False


TWEAK_GROUPS = [
    ListBoxTweakGroup(_("General"),
        GSettingsSwitchTweak(_("Animations"), "org.gnome.desktop.interface", "enable-animations"),
        IgnoreLidSwitchTweak(),
        # Don't show this setting in the Ubuntu session since this setting is in gnome-control-center there
        GSettingsSwitchTweak(_("Over-Amplification"), "org.gnome.desktop.sound", "allow-volume-above-100-percent",
            desc=_("Allows raising the volume above 100%. This can result in a loss of audio quality; it is better to increase application volume settings, if possible."), loaded=_shell_not_ubuntu),
    ),
]
