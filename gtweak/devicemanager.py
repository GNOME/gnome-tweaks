# Copyright (c) 2024 Evan Welsh
# SPDX-License-Identifier: GPL-3.0+
# License-Filename: LICENSES/GPL-3.0

from gi.repository import GUdev

# Inspired by panels/common/gsd-device-manager.c in GNOME Settings
# https://gitlab.gnome.org/GNOME/gnome-control-center/-/blob/6d2add0e30538692c151e5fa0bd94ae9bece7690/panels/common/gsd-device-manager.c

UDEV_ID_INPUT_MOUSE = "ID_INPUT_MOUSE"
UDEV_ID_INPUT_KEYBOARD = "ID_INPUT_KEYBOARD"
UDEV_ID_INPUT_TOUCHPAD = "ID_INPUT_TOUCHPAD"
UDEV_ID_INPUT_POINTING_STICK = "ID_INPUT_POINTINGSTICK"

UDEV_IDS = [
    UDEV_ID_INPUT_MOUSE,
    UDEV_ID_INPUT_KEYBOARD,
    UDEV_ID_INPUT_TOUCHPAD,
    UDEV_ID_INPUT_POINTING_STICK,
]

def udev_device_is_evdev(device):
    device_file = device.get_device_file()
    if device_file is None or "/event" not in device_file:
        return False
    
    return device.get_property_as_boolean("ID_INPUT")


def get_input_devices():
    udev_client = GUdev.Client()
    devices = udev_client.query_by_subsystem ("input")
    
    return [device for device in devices if udev_device_is_evdev(device)]


def udev_device_get_device_types (device):
    types = set()

    for id in UDEV_IDS:
        if device.get_property_as_boolean(id):
            types.add(id)

    return types


def udev_device_id_is_present(id):
    for device in get_input_devices():
        if id in udev_device_get_device_types(device):
              return True

    return False


def pointing_stick_is_present():
    return udev_device_id_is_present(UDEV_ID_INPUT_POINTING_STICK)


def touchpad_is_present():
    return udev_device_id_is_present(UDEV_ID_INPUT_TOUCHPAD)