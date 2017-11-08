# Copyright (c) 2013 Red Hat, Inc.
# Author: Joaquim Rocha <jrocha@redhat.com>
# SPDX-License-Identifier: GPL-3.0+
# License-Filename: LICENSES/GPL-3.0

from gtweak.tweakmodel import TweakGroup
from gtweak.widgets import GSettingsSwitchTweak
import subprocess
import configparser
import io

def N_(x): return x

LIST_WACOM_DEVICES_CMD = 'libwacom-list-local-devices'
DEVICE_MATCH_LINE = 'DeviceMatch'
DEVICE_SECTION = _("Device")
MACHINE_ID_PATH = '/etc/machine-id'
SCHEMA_NAME = 'org.gnome.settings-daemon.peripherals.wacom'
SCHEMA_PATH = '/org/gnome/settings-daemon/peripherals/wacom/%s-%s/'
TABLET_PC_KEY = 'tablet-pc-button'

class WacomGroup(TweakGroup):

    def __init__(self):
        TweakGroup.__init__(self, N_("Wacom"))

        try:
            configs = WacomConfigs()
        except:
            return

        tweaks = ()
        for config in configs.get_matched_isd_devices():
            summary = '%(tablet_name)s: Tablet PC mode' % {'tablet_name': config.get(DEVICE_SECTION, 'Name')}
            tweaks += (WacomSwitchTweak(config,
                                        configs.machine_id,
                                        SCHEMA_NAME,
                                        TABLET_PC_KEY,
                                        schema_filename=SCHEMA_NAME + '.gschema.xml',
                                        summary=summary),
                       )
        self.set_tweaks(*tweaks)

class WacomConfigs(object):

    def __init__(self):
        self._configs = self._load_configs()
        self.machine_id = self._get_machine_id()
        if not self._configs or not self.machine_id:
            raise Exception("Couldn't get Wacom devices' configurations")

    def _get_machine_id(self):
        try:
            machine_file = open(MACHINE_ID_PATH, 'r')
        except IOError:
            machine_id = ''
        else:
            machine_id = machine_file.read().strip()
            machine_file.close()
        return machine_id

    def _load_configs(self):
        proc = subprocess.Popen(LIST_WACOM_DEVICES_CMD,
                                stdout=subprocess.PIPE)
        configs = self._output_to_config(proc.stdout.readlines())
        proc.stdout.close()
        proc.wait()
        return configs

    def get_matched_isd_devices(self):
        '''Returns a tuple with the device's name and matched ID'''
        if not self._configs:
            return []
        return [config for config in self._configs \
                if config.get(DEVICE_SECTION, 'IntegratedIn')]

    def _output_to_config(self, output_lines):
        configs = ['']
        configs_dict = {}
        for line in output_lines:
            if line.startswith('-' * 5):
                configs.append('')
            else:
                configs[-1] += line
        for item in configs:
            if item:
                config = self._text_to_config(item)
                match_id = config.get(DEVICE_SECTION, DEVICE_MATCH_LINE)
                # Use a dict to discard possible repeated devices
                configs_dict[match_id] = config
        return list(configs_dict.values())

    def _text_to_config(self, text):
        config = configparser.RawConfigParser(allow_no_value=True)
        config.readfp(io.BytesIO(text))
        return config

class WacomSwitchTweak(GSettingsSwitchTweak):

    def __init__(self, config, machine_id, schema_name, key_name, **options):
        name = config.get(DEVICE_SECTION, 'Name')
        match_id = config.get(DEVICE_SECTION, DEVICE_MATCH_LINE).strip(';')
        self._schema_path = SCHEMA_PATH % (machine_id, match_id)
        GSettingsSwitchTweak.__init__(self,
                                      schema_name,
                                      key_name,
                                      schema_path = self._schema_path,
                                      **options)
wg = WacomGroup()
if wg.tweaks:
    TWEAK_GROUPS = (wg,)
