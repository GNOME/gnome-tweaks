GNOME Tweaks
=============================

[Repository](https://gitlab.gnome.org/GNOME/gnome-tweaks)

[Bug Tracker](https://gitlab.gnome.org/GNOME/gnome-tweaks/issues)

## Supported Desktops

Tweaks is designed for GNOME Shell but can be used in other desktops.

Some few features will be missing when Tweaks is run without gnome-shell.

## Build

The only build-time dependency is [meson](https://mesonbuild.com/).

    meson builddir
    ninja -C builddir
    ninja -C builddir install

### Runtime Dependencies

- Python 3
- pygobject
- gnome-settings-daemon
- sound-theme-freedesktop

- GIR files and libraries from:

  - GLib
  - GTK 4
  - gnome-desktop
  - libadwaita
  - libnotify
  - Pango
  - gsettings-desktop-schemas
  - libgudev

- GSettings Schemas from:
  - gsettings-desktop-schemas
  - gnome-shell
  - mutter

### Running

- If you wish to run the application uninstalled, execute;

  ./gnome-tweaks [-p /path/to/jhbuild/prefix/]

## License

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later version.

data/org.gnome.tweaks.appdata.xml.in is licensed under the [Creative Commons
CC0-1.0](https://creativecommons.org/publicdomain/zero/1.0/legalcode) license.
