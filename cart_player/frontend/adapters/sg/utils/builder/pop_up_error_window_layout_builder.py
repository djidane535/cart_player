from typing import List

import PySimpleGUI as sg

from .component_builders import ButtonBuilder, TextBuilder


class PopUpErrorWindowLayoutBuilder:
    """Builder for pop-up error window layout."""

    # >> Structure <<
    # +----------------+
    # + <MESSAGE>      +
    # + <CLOSE BUTTON> +
    # +----------------+
    #
    @staticmethod
    def build(message: str, close_button_name: str) -> List[sg.Element]:
        """Return the organized list of components"""
        return [
            [TextBuilder.build(message)],
            [sg.Push(), ButtonBuilder.build_generic_error_close_button(close_button_name)],
        ]
