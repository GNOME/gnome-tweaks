GNOME TWEAKS
================


BUILD
-----
The only build-time dependency is [meson](http://mesonbuild.com/).

    meson builddir
    ninja -C builddir
    ninja -C builddir install

RUNTIME DEPENDENCIES
--------------------
* Python3
* pygobject (>= 3.10)
* gnome-settings-daemon

* GIR files and libraries from:
  - GLib
  - GTK+ 3 (>= 3.12)
  - gnome-desktop
  - libsoup
  - libnotify
  - Pango

* GSettings Schemas from:
  - gsettings-desktop-schemas (>= 3.24)
  - gnome-shell (>= 3.24)
  - mutter
  - nautilus

* Optional:
   - gnome-software (for links from GNOME Shell Extensions page)

RUNNING
-------
 * If you wish to run the application uninstalled, execute;

    ./gnome-tweaks [-p /path/to/jhbuild/prefix/]

SUPPORTED DESKTOPS
------------------
Tweaks is designed for GNOME Shell but can be used in other desktops.
A few features will be missing when Tweaks is run on a different desktop.

TODO
----
 * I'm not sure if the TweakGroup layer is necessary, and it makes
   it hard to categorise things. Perhaps go to a named factory approach
 * Do some more things lazily to improve startup speed

HOMEPAGE
--------
https://wiki.gnome.org/Apps/Tweaks

DEVELOPMENT REPOSITORY
----------------------
https://gitlab.gnome.org/GNOME/gnome-tweaks

BUGS
----
https://gitlab.gnome.org/GNOME/gnome-tweaks/issues

LICENSE
-------
This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later version.

data/org.gnome.tweaks.appdata.xml.in is licensed under the Creative Commons
CC0-1.0 license.
