from typing import List

import PySimpleGUI as sg

from cart_player.frontend.resources import app_icon_filepath

from .component_builders import ButtonBuilder, ComponentKey, ImageBuilder


class PopUpWindowSelectorBuilder:
    """Builder for pop-up window selector."""

    # >> Structure <<
    # +--------------------------------------------------------------------------------------------+
    # + APP_ICON | PLAY_SELECTOR_BUTTON | DATA_SELECTOR_BUTTON | <PUSH> | SETTINGS_SELECTOR_BUTTON +
    # +--------------------------------------------------------------------------------------------+
    #
    @staticmethod
    def build() -> List[sg.Element]:
        """Return the organized list of components"""
        return [
            ImageBuilder.build(app_icon_filepath),
            ButtonBuilder.build_layout_selector_button(
                "PLAY",
                tooltip="Play to your game.",
                key=ComponentKey.PLAY_SELECTOR_BUTTON,
            ),
            ButtonBuilder.build_layout_selector_button(
                "DATA",
                tooltip="Data management.",
                key=ComponentKey.DATA_SELECTOR_BUTTON,
            ),
            sg.Push(),
            ButtonBuilder.build_layout_selector_button(
                "SETTINGS",
                tooltip="App settings.",
                key=ComponentKey.SETTINGS_SELECTOR_BUTTON,
            ),
        ]
