# Copyright (c) 2011 John Stowers
# SPDX-License-Identifier: GPL-3.0+
# License-Filename: LICENSES/GPL-3.0

from gtweak.widgets import ListBoxTweakGroup, GSettingsSwitchTweak, GSettingsComboEnumTweak, GSettingsFileChooserButtonTweak, Title

dicons = GSettingsSwitchTweak(_("Show Icons"),"org.gnome.desktop.background","show-desktop-icons")

TWEAK_GROUPS = [
    ListBoxTweakGroup(_("Desktop"),
        Title(_("Icons on Desktop"), "", uid="title-theme", top=True),
        dicons,
        GSettingsSwitchTweak(_("Home"),"org.gnome.nautilus.desktop", "home-icon-visible", depends_on=dicons, schema_filename="org.gnome.nautilus.gschema.xml"),
        GSettingsSwitchTweak(_("Network Servers"),"org.gnome.nautilus.desktop", "network-icon-visible", depends_on=dicons, schema_filename="org.gnome.nautilus.gschema.xml"),
        GSettingsSwitchTweak(_("Trash"),"org.gnome.nautilus.desktop", "trash-icon-visible", depends_on=dicons, schema_filename="org.gnome.nautilus.gschema.xml"),
        GSettingsSwitchTweak(_("Mounted Volumes"),"org.gnome.nautilus.desktop", "volumes-visible", depends_on=dicons, schema_filename="org.gnome.nautilus.gschema.xml"),
        Title(_("Background"), "", uid="title-theme"),
        GSettingsFileChooserButtonTweak(_("Image"),"org.gnome.desktop.background", "picture-uri", local_only=True, mimetypes=["application/xml","image/png","image/jpeg"]),
        GSettingsComboEnumTweak(_("Adjustment"),"org.gnome.desktop.background", "picture-options"),
        Title(_("Lock Screen"), "", uid="title-theme"),
        GSettingsFileChooserButtonTweak(_("Image"),"org.gnome.desktop.screensaver", "picture-uri", local_only=True, mimetypes=["application/xml","image/png","image/jpeg"]),
        GSettingsComboEnumTweak(_("Adjustment"),"org.gnome.desktop.screensaver", "picture-options"),
        #Title(_("Files"), ""),
        #GSettingsSwitchTweak(_("Use location entry"), "org.gnome.nautilus.preferences", "always-use-location-entry",schema_filename="org.gnome.nautilus.gschema.xml"),

    )
]
