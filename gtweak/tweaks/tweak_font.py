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

from gtweak.tweakmodel import Tweak, TweakGroup
from gtweak.widgets import GSettingsRangeTweak, GSettingsFontButtonTweak, GConfFontButtonTweak, GSettingsComboTweak, build_horizontal_sizegroup

sg = build_horizontal_sizegroup()

TWEAK_GROUPS = (
        TweakGroup(
            _("Fonts"),
            GSettingsRangeTweak("org.gnome.desktop.interface", "text-scaling-factor", adjustment_step=0.1, size_group=sg),
            GSettingsFontButtonTweak("org.gnome.desktop.interface", "font-name", size_group=sg),
            GSettingsFontButtonTweak("org.gnome.desktop.interface", "document-font-name", size_group=sg),
            GSettingsFontButtonTweak("org.gnome.desktop.interface", "monospace-font-name", size_group=sg),
            GConfFontButtonTweak("/apps/metacity/general/titlebar_font", str, size_group=sg),
            GSettingsComboTweak("org.gnome.settings-daemon.plugins.xsettings", "hinting",
                [(i, i.title()) for i in ("none", "slight", "medium", "full")], size_group=sg),
            GSettingsComboTweak("org.gnome.settings-daemon.plugins.xsettings", "antialiasing",
                [(i, i.title()) for i in ("none", "grayscale", "rgba")], size_group=sg)),
)
