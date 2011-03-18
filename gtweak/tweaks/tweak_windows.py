from gtweak.tweakmodel import TweakGroup
from gtweak.widgets import GConfComboTweak, build_horizontal_sizegroup

class ActionClickTitlebarTweak(GConfComboTweak):
    def __init__(self, key_name, **options):

        #from the metacity schema
        schema_options = ('toggle_shade', 'toggle_maximize', 'toggle_maximize_horizontally',
                          'toggle_maximize_vertically', 'minimize', 'shade', 'menu', 'lower', 'none')

        GConfComboTweak.__init__(self,
            key_name,
            str,
            [(o, o.replace("_"," ").title()) for o in schema_options],
            **options)

sg = build_horizontal_sizegroup()

TWEAK_GROUPS = (
        TweakGroup(
            "Windows",
            ActionClickTitlebarTweak("/apps/metacity/general/action_double_click_titlebar", size_group=sg),
            ActionClickTitlebarTweak("/apps/metacity/general/action_middle_click_titlebar", size_group=sg),
            ActionClickTitlebarTweak("/apps/metacity/general/action_right_click_titlebar", size_group=sg)),
)
