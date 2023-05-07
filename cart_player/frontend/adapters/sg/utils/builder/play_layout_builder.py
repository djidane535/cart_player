from typing import List

import PySimpleGUI as sg

from ..app_context import AppContext
from .component_builders import ButtonBuilder, ComponentKey, FrameBuilder, TextBuilder
from .utils import build_existing_saves


class PlayLayoutBuilder:
    """Builder for data layout."""

    # >> Structure <<
    # +---------------+
    # + LAUNCH_BUTTON +
    # +---------------+
    #
    @staticmethod
    def build(context: AppContext) -> List[sg.Element]:
        """Return the organized list of components"""
        enable_launch_button = PlayLayoutBuilder.can_enable_launch_button(context)
        enable_end_session_button = PlayLayoutBuilder.can_enable_end_session_button(context)
        existing_saves: List[str] = build_existing_saves(context)
        return [
            [
                FrameBuilder.build(
                    "Settings",
                    [
                        [
                            TextBuilder.build("Save file"),
                            sg.Combo(
                                existing_saves,
                                default_value=existing_saves[0],
                                expand_x=True,
                                size=(40, 0),
                                key=ComponentKey.PLAY_SAVE_BOX_SAVE_NAMES_COMBO,
                            ),
                        ]
                    ],
                )
            ],
            [
                sg.Push(),
                ButtonBuilder.build(
                    "LAUNCH",
                    "Launch your game.",
                    disabled=not enable_launch_button,
                    key=ComponentKey.LAUNCH_BUTTON,
                ),
                ButtonBuilder.build(
                    "END SESSION",
                    "End your game session.",
                    disabled=not enable_end_session_button,
                    key=ComponentKey.END_SESSION,
                ),
                sg.Push(),
            ],
        ]

    @staticmethod
    def can_enable_launch_button(context: AppContext) -> bool:
        return not context.in_game_session and context.cart_inserted and context.is_game_installed

    @staticmethod
    def can_enable_end_session_button(context: AppContext) -> bool:
        return context.in_game_session and context.cart_inserted and context.is_game_installed
