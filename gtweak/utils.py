# Copyright (c) 2011 John Stowers
# SPDX-License-Identifier: GPL-3.0+
# License-Filename: LICENSES/GPL-3.0

import os.path
import logging
import tempfile
import shutil
import subprocess
import glob
import itertools
import logging

import gi
gi.require_version("Notify", "0.7")
from gi.repository import GLib
from gi.repository import Gio
from gi.repository import Notify

import gtweak
from gtweak.gsettings import GSettingsMissingError, GSettingsSetting


def singleton(cls):
    """
    Singleton decorator that works with GObject derived types. The 'recommended'
    python one - http://wiki.python.org/moin/PythonDecoratorLibrary#Singleton
    does not (interacts badly with GObjectMeta
    """
    instances = {}

    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return getinstance


def make_combo_list_with_default(opts, default, title=True, default_text=None):
    """
    Turns a list of values into a list of value,name (where name is the
    display name a user will see in a combo box). If a value is opt is
    equal to that supplied in default the display name for that value is
    modified to "value <i>(default)</i>"

    @opts: a list of value
    @returns: a list of 2-tuples (value, name)
    """
    themes = []
    for t in opts:
        if t.lower() == "default" and t != default:
            # some themes etc are actually called default. Ick. Dont show them if they
            # are not the actual default value
            continue

        if title and len(t):
            name = t[0].upper() + t[1:]
        else:
            name = t

        if t == default:
            # indicates the default theme, e.g Adwaita (default)
            name = default_text or _("%s (default)") % name

        themes.append((t, name))
    return themes


def walk_directories(dirs, filter_func):
    valid = []
    try:
        for thdir in dirs:
            if os.path.isdir(thdir):
                for t in os.listdir(thdir):
                    if filter_func(os.path.join(thdir, t)):
                        valid.append(t)
    except:
        logging.critical("Error parsing directories", exc_info=True)
    return valid


def extract_zip_file(z, members_path, dest):
    """ returns (true_if_extracted_ok, true_if_updated) """
    tmp = tempfile.mkdtemp()
    tmpdest = os.path.join(tmp, members_path)

    ok = True
    updated = False
    try:
        if os.path.exists(dest):
            shutil.rmtree(dest)
            updated = True
        z.extractall(tmp)
        shutil.copytree(tmpdest, dest)
    except OSError:
        ok = False
        logging.warning("Error extracting zip", exc_info=True)

    if ok:
        logging.info("Extracted zip to %s, copied to %s" % (tmpdest, dest))

    return ok, updated


def execute_subprocess(cmd_then_args, block=True):
    p = subprocess.Popen(
            cmd_then_args,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, close_fds=True,
            universal_newlines=True)
    if block:
        stdout, stderr = p.communicate()
        return stdout, stderr, p.returncode


def get_resource_dirs(resource):
    """Returns a list of all known resource dirs for a given resource.

    :param str resource:
        Name of the resource (e.g. "themes")
    :return:
        A list of resource dirs
    """
    dirs = [os.path.join(dir, resource)
            for dir in itertools.chain(GLib.get_system_data_dirs(),
                                       (gtweak.DATA_DIR,
                                        GLib.get_user_data_dir()))]
    dirs += [os.path.join(os.path.expanduser("~"), ".{}".format(resource))]

    return [dir for dir in dirs if os.path.isdir(dir)]


@singleton
class AutostartManager:

    @staticmethod
    def get_desktop_files():
        return [a.get_filename() for a in Gio.app_info_get_all()]

    @staticmethod
    def get_user_autostart_files():
        return glob.glob(
                    os.path.join(
                        GLib.get_user_config_dir(), "autostart", "*.desktop"))

    @staticmethod
    def get_system_autostart_files():
        f = []
        for d in GLib.get_system_config_dirs():
            f.extend(glob.glob(os.path.join(d, "autostart", "*.desktop")))
        return f


class AutostartFile:
    def __init__(self, appinfo, autostart_desktop_filename="", exec_cmd="", extra_exec_args=""):
        if appinfo:
            self._desktop_file = appinfo.get_filename()
            self._autostart_desktop_filename = autostart_desktop_filename or os.path.basename(self._desktop_file)
            self._create_file = False
        elif autostart_desktop_filename:
            self._desktop_file = None
            self._autostart_desktop_filename = autostart_desktop_filename
            self._create_file = True
        else:
            raise Exception("Need either an appinfo or a file name")

        self._exec_cmd = exec_cmd
        if extra_exec_args:
            self._extra_exec_args = " %s\n" % extra_exec_args
        else:
            self._extra_exec_args = "\n"

        user_autostart_dir = os.path.join(GLib.get_user_config_dir(), "autostart")
        os.makedirs(user_autostart_dir, exist_ok=True)

        self._user_autostart_file = os.path.join(user_autostart_dir, self._autostart_desktop_filename)

        if self._desktop_file:
            logging.debug("Found desktop file: %s" % self._desktop_file)
        logging.debug("User autostart desktop file: %s" % self._user_autostart_file)

    def _create_user_autostart_file(self):
        f = open(self._user_autostart_file, "w")
        f.write("[Desktop Entry]\nType=Application\nName=%s\nExec=%s\n" %
                (self._autostart_desktop_filename[0:-len('.desktop')], self._exec_cmd + self._extra_exec_args))
        f.close()

    def is_start_at_login_enabled(self):
        if os.path.exists(self._user_autostart_file):
            # prefer user directories first
            # if it contains X-GNOME-Autostart-enabled=false then it has
            # has been disabled by the user in the session applet, otherwise
            # it is enabled
            return open(self._user_autostart_file).read().find("X-GNOME-Autostart-enabled=false") == -1
        else:
            # check the system directories
            for f in AutostartManager().get_system_autostart_files():
                if os.path.basename(f) == self._autostart_desktop_filename:
                    return True
        return False

    def update_start_at_login(self, update):

        if os.path.exists(self._user_autostart_file):
            logging.info("Removing user autostart file %s" % self._user_autostart_file)
            os.remove(self._user_autostart_file)

        if update:
            if (not self._desktop_file) or (not os.path.exists(self._desktop_file)):
                if self._create_file:
                    self._create_user_autostart_file()
                else:
                    logging.critical("Could not find desktop file: %s" % self._desktop_file)
                return

            logging.info("Adding autostart %s" % self._user_autostart_file)
            #copy the original file to the new file, but add the extra exec args
            old = open(self._desktop_file, "r")
            new = open(self._user_autostart_file, "w")

            for l in old.readlines():
                if l.startswith("Exec="):
                    if self._exec_cmd:
                        new.write("Exec=%s\n" % self._exec_cmd)
                    else:
                        new.write(l[0:-1])
                        new.write(self._extra_exec_args)
                else:
                    new.write(l)

            old.close()
            new.close()


class SchemaList:
    @classmethod
    def setup(cls):
        cls.__list = []

    @classmethod
    def get(cls):
        return cls.__list

    @classmethod
    def insert(cls, key_name, schema_id = None, schema_name = None, schema_dir = None):
        v = [key_name, (schema_id, schema_name, schema_dir)]
        cls.__list.append(v)

    @classmethod
    def reset(cls):
        for key_name, (schema_id, schema_name, schema_dir) in cls.__list:
            try:
              s = GSettingsSetting(schema_id=schema_id, schema_dir=schema_dir, schema_name=schema_name)
              s.reset(key_name)
            except GSettingsMissingError:
              logging.warn(f"Could not reset {key_name}, {schema_id or schema_name} is not installed.")


SchemaList.setup()

@singleton
class XSettingsOverrides:

    VARIANT_TYPES = {
        'Gtk/ShellShowsAppMenu': GLib.Variant.new_int32,
        'Gtk/EnablePrimaryPaste': GLib.Variant.new_int32,
        'Gdk/WindowScalingFactor': GLib.Variant.new_int32,
    }

    def __init__(self):
        # Ensure we don't error out
        try:
            self._settings = GSettingsSetting(schema='org.gnome.settings-daemon.plugins.xsettings')
        except:
            self._settings = None
            logging.warn("org.gnome.settings-daemon.plugins.xsettings not installed or running")
        
        if self._settings:
            self._variant = self._settings.get_value("overrides")

    def _dup_variant_as_dict(self):
        items = {}
        for k in list(self._variant.keys()):
            try:
                # variant override doesnt support .items()
                v = self._variant[k]
                items[k] = self.VARIANT_TYPES[k](v)
            except KeyError:
                pass
        return items

    def _dup_variant(self):
        return GLib.Variant('a{sv}', self._dup_variant_as_dict())

    def _set_override(self, name, v):
        items = self._dup_variant_as_dict()
        items[name] = self.VARIANT_TYPES[name](v)
        n = GLib.Variant('a{sv}', items)
        self._settings.set_value('overrides', n)
        self._variant = self._settings.get_value("overrides")

    def _get_override(self, name, default):
        try:
            return self._variant[name]
        except KeyError:
            return default

    # while I could store meta type information in the VARIANT_TYPES
    # dict, its easiest to do default value handling and missing value
    # checks in dedicated functions
    def set_shell_shows_app_menu(self, v):
        self._set_override('Gtk/ShellShowsAppMenu', int(v))

    def get_shell_shows_app_menu(self):
        return self._get_override('Gtk/ShellShowsAppMenu', True)

    def set_enable_primary_paste(self, v):
        self._set_override('Gtk/EnablePrimaryPaste', int(v))

    def get_enable_primary_paste(self):
        return self._get_override('Gtk/EnablePrimaryPaste', True)

    def set_window_scaling_factor(self, v):
        self._set_override('Gdk/WindowScalingFactor', int(v))

    def get_window_scaling_factor(self):
        return self._get_override('Gdk/WindowScalingFactor', 1)


class Notification:
    def __init__(self, summary, body):
        if Notify.is_initted() or Notify.init(_("GNOME Tweaks")):
            self.notification = Notify.Notification.new(
                                    summary,
                                    body,
                                    'gnome-tweaks'
            )
            self.notification.set_hint(
                                "desktop-entry",
                                GLib.Variant('s', gtweak.APP_ID))
            self.notification.show()
        else:
            raise Exception("Not Supported")


@singleton
class LogoutNotification:
    def __init__(self):
        if Notify.is_initted() or Notify.init(_("GNOME Tweaks")):
            self.notification = Notify.Notification.new(
                                _("Configuration changes require restart"),
                                _("Your session needs to be restarted for settings to take effect"),
                                'gnome-tweaks')
            self.notification.add_action(
                                "restart",
                                _("Restart Session"),
                                self._logout, None, None)
            self.notification.set_hint(
                                "desktop-entry",
                                GLib.Variant('s', gtweak.APP_ID))
            self.notification.show()
        else:
            raise Exception("Not Supported")

    def _logout(self, btn, action, user_data, unknown):
        d = Gio.bus_get_sync(Gio.BusType.SESSION, None)
        proxy = Gio.DBusProxy.new_sync(
                       d, Gio.DBusProxyFlags.NONE, None,
                       'org.gnome.SessionManager',
                       '/org/gnome/SessionManager',
                       'org.gnome.SessionManager',
                       None)
        proxy.Logout('(u)', 0)
