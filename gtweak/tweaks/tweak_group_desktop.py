# Copyright (c) 2011 John Stowers
# SPDX-License-Identifier: GPL-3.0+
# License-Filename: LICENSES/GPL-3.0

from gtweak.widgets import ListBoxTweakGroup, GSettingsSwitchTweak, Title

dicons = GSettingsSwitchTweak(_("Show Icons"),"org.gnome.desktop.background","show-desktop-icons")

# show-desktop-icons is in gsettings-desktop-schemas, but it won't actually
# *work* unless we have a version of Nautilus that still has the ability to
# draw the desktop; use one of the settings that was present in that version
# to probe for it.
home = GSettingsSwitchTweak(_("Home"),"org.gnome.nautilus.desktop",
                            "home-icon-visible", depends_on=dicons,
                            schema_filename="org.gnome.nautilus.gschema.xml")

TWEAK_GROUPS = []

if home.loaded:
    TWEAK_GROUPS.append(ListBoxTweakGroup(_("Desktop"),
        Title(_("Icons on Desktop"), "", uid="title-theme", top=True),
        dicons,
        home,
        GSettingsSwitchTweak(_("Network Servers"),"org.gnome.nautilus.desktop", "network-icon-visible", depends_on=dicons, schema_filename="org.gnome.nautilus.gschema.xml"),
        GSettingsSwitchTweak(_("Trash"),"org.gnome.nautilus.desktop", "trash-icon-visible", depends_on=dicons, schema_filename="org.gnome.nautilus.gschema.xml"),
        GSettingsSwitchTweak(_("Mounted Volumes"),"org.gnome.nautilus.desktop", "volumes-visible", depends_on=dicons, schema_filename="org.gnome.nautilus.gschema.xml"),
    ))
