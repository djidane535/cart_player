from typing import List

import PySimpleGUI as sg

from .component_builders import ButtonBuilder, TextBuilder


class PopUpWarningWindowLayoutBuilder:
    """Builder for pop-up warning window layout."""

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
            [sg.Push(), ButtonBuilder.build_generic_warning_close_button(close_button_name)],
        ]
