# Copyright (c) 2011 John Stowers
# SPDX-License-Identifier: GPL-3.0+
# License-Filename: LICENSES/GPL-3.0

import json
import logging

import gi
gi.require_version("Soup", "2.4")
from gi.repository import GObject
from gi.repository import Soup


class ExtensionsDotGnomeDotOrg(GObject.GObject):

    __gsignals__ = {
      "got-extensions": (GObject.SignalFlags.RUN_FIRST, GObject.TYPE_NONE,
                         (GObject.TYPE_PYOBJECT,)),
      "got-extension-info": (GObject.SignalFlags.RUN_FIRST, GObject.TYPE_NONE,
                             (GObject.TYPE_PYOBJECT, GObject.TYPE_STRING)),
    }

    def __init__(self, shell_version_tuple):
        GObject.GObject.__init__(self)
        self._session = Soup.Session.new()

        self._shell_version_tuple = shell_version_tuple
        self._extensions = {}

    def _query_extensions_finished(self, msg, url):
        if msg.status_code == 200:
            # server returns a list of extensions which may contain duplicates, dont know
            resp = json.loads(msg.response_body.data)
            print(resp)
            for e in resp["extensions"]:
                self._extensions[e["uuid"]] = e
            self.emit("got-extensions", self._extensions)

    def _query_extension_info_finished(self, msg, uuid):
        if msg.status_code == 200:
            self.emit("got-extension-info", json.loads(msg.response_body.data), uuid)

    def query_extensions(self):
        url = "https://extensions.gnome.org/extension-query/?"

        ver = self._shell_version_tuple
        if ver[1] % 2:
            # if this is a development version (odd) then query the full version
            url += "shell_version=%d.%d.%d&" % ver
        else:
            # else query in point releases up to the current version
            # and filter duplicates from the reply
            url += "shell_version=%d.%d&" % (ver[0], ver[1])
            for i in range(1, ver[2]+1):
                url += "shell_version=%d.%d.%d&" % (ver[0], ver[1], i)
        # non-paginated
        url += "n_per_page=-1"

        logging.debug("Query URL: %s" % url)
        message = Soup.Message.new('GET', url)
        message.connect("finished", self._query_extensions_finished, url)
        self._session.queue_message(message, None, None)

    def query_extension_info(self, extension_uuid):
        if extension_uuid in self._extensions:
            print("CACHED")
            self.emit("got-extension-info", self._extensions[extension_uuid])
            return

        url = "https://extensions.gnome.org/extension-info/?uuid=%s" % extension_uuid
        logging.debug("Query URL: %s" % url)
        message = Soup.Message.new('GET', url)
        message.connect("finished", self._query_extension_info_finished, extension_uuid)
        self._session.queue_message(message, None, None)

    def get_download_url(self, extinfo):
        url = "https://extensions.gnome.org/download-extension/%s.shell-extension.zip?version_tag=%d"
        # version tag is the pk in the shell_version_map
        # url = url % (extinfo["uuid"],


if __name__ == "__main__":
    import pprint
    from gi.repository import Gtk

    def _got_ext(ego, extensions):
        print("="*80)
        pprint.pprint(list(extensions.values()))

    def _got_ext_info(ego, extension):
        pprint.pprint(extension)

    logging.basicConfig(format="%(levelname)-8s: %(message)s", level=logging.DEBUG)

    e = ExtensionsDotGnomeDotOrg((3, 4, 1))

    e.connect("got-extensions", _got_ext)
    e.connect("got-extension-info", _got_ext_info)

    e.query_extensions()
    # e.query_extensions((3, 4, 0))
    # e.query_extensions((3, 3, 2))
    e.query_extension_info("user-theme@gnome-shell-extensions.gcampax.github.com")

    Gtk.main()
