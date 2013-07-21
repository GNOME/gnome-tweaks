# This file is part of gnome-tweak-tool.
#
# Copyright (c) 2011 John Stowers
#
# gnome-tweak-tool is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# gnome-tweak-tool is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with gnome-tweak-tool.  If not, see <http://www.gnu.org/licenses/>.

from gi.repository import Gtk

from gtweak.tweakmodel import Tweak, TWEAK_GROUP_FONTS, TWEAK_SORT_FIRST, TWEAK_SORT_LAST
from gtweak.widgets import GSettingsSpinButtonTweak, GSettingsFontButtonTweak, GSettingsComboTweak

TWEAKS = (
    GSettingsFontButtonTweak("Interface","org.gnome.desktop.interface", "font-name", group_name=TWEAK_GROUP_FONTS),
    GSettingsFontButtonTweak("Documents", "org.gnome.desktop.interface", "document-font-name", group_name=TWEAK_GROUP_FONTS),
    GSettingsFontButtonTweak("Monospace", "org.gnome.desktop.interface", "monospace-font-name", group_name=TWEAK_GROUP_FONTS),
    GSettingsFontButtonTweak("Window Titles","org.gnome.desktop.wm.preferences", "titlebar-font", group_name=TWEAK_GROUP_FONTS, sort=TWEAK_SORT_FIRST),
    GSettingsComboTweak("Hinting","org.gnome.settings-daemon.plugins.xsettings", "hinting",
        [(i, i.title()) for i in ("none", "slight", "medium", "full")], group_name=TWEAK_GROUP_FONTS, sort=TWEAK_SORT_LAST),
    GSettingsComboTweak("Antialiasing","org.gnome.settings-daemon.plugins.xsettings", "antialiasing",
        [(i, i.title()) for i in ("none", "grayscale", "rgba")], group_name=TWEAK_GROUP_FONTS,sort=TWEAK_SORT_LAST),
)
