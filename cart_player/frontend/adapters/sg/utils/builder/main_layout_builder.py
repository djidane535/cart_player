import os
from collections import defaultdict
from pathlib import Path
from typing import List

import PySimpleGUI as sg

from cart_player.frontend.adapters.sg.utils.text import wrap_text

from ..app_context import AppContext
from .component_builders import ButtonBuilder, ComponentKey, FrameBuilder, ImageBuilder, TextBuilder

GAME_IMAGE_SQUARE_SIZE = 256
KEY_TEXT_WIDTH = 15 if os.name == 'nt' else 10
VALUE_TEXT_WIDTH = 50 if os.name == 'nt' else 75
VALUE_TEXT_MAX_LINES_PER_KEY = defaultdict(lambda: 1)
VALUE_TEXT_MAX_LINES_PER_KEY[ComponentKey.GAME_CART_BOX_VALUE_DESCRIPTION] = 9
POP_UP_MESSAGE_WIDTH = 200 if os.name == 'nt' else 150


class MainLayoutBuilder:
    """Builder for play layout."""

    @staticmethod
    def default_game_cart_box_image_filepath() -> Path:
        from cart_player.frontend.resources import gamecart_placeholder_filepath

        return Path(gamecart_placeholder_filepath)

    @staticmethod
    def default_game_cart_box_info_value_text() -> str:
        return "NO DATA"

    # >> WINDOW  structure <<
    # +--------+
    # + HEADER +
    # + BODY   +
    # +--------+
    #
    @staticmethod
    def build(context: AppContext) -> List[sg.Element]:
        """Return the organized list of components"""
        return [
            MainLayoutBuilder._build_body_components(),
            MainLayoutBuilder._build_header_components(),
        ]

    # >> HEADER structure <<
    # +-------------------------+
    # + <PUSH> | REFRESH_BUTTON +
    # +-------------------------+
    #
    @staticmethod
    def _build_header_components() -> List[sg.Element]:
        """Return the organized list of header components."""
        return [
            sg.Push(),
            ButtonBuilder.build(
                "REFRESH",
                "Refresh app and game metadata box.",
                key=ComponentKey.REFRESH_BUTTON,
            ),
        ]

    # >> BODY structure <<
    # +-----------------+
    # + GAME_METADATA_BOX   +
    # +-----------------+
    #
    @staticmethod
    def _build_body_components() -> List[sg.Element]:
        """Return the organized list of body components."""
        return MainLayoutBuilder._build_gamecart_box_components()

    # >> GAMECART_BOX structure <<
    # +--------------------------------+
    # + GAMECART_IMAGE | GAMECART_INFO +
    # +--------------------------------+
    #
    @staticmethod
    def _build_gamecart_box_components() -> List[sg.Element]:
        """Build game metadata box components."""
        return [
            MainLayoutBuilder._build_gamecart_image_components(),
            MainLayoutBuilder._build_gamecart_info_components(),
        ]

    @staticmethod
    def _build_gamecart_image_components() -> sg.Element:
        """Build game cart image components."""
        return FrameBuilder.build(
            "Game",
            [
                [sg.Push()],
                [
                    sg.Push(),
                    ImageBuilder.build(
                        str(MainLayoutBuilder.default_game_cart_box_image_filepath()),
                        square_size=GAME_IMAGE_SQUARE_SIZE,
                        key=ComponentKey.GAME_CART_BOX_IMAGE,
                    ),
                    sg.Push(),
                ],
                [sg.Push()],
            ],
        ).set_expand_y()

    # >> GAMECART_INFO structure <<
    # +----------------+
    # + <KEY> | <INFO> +
    # + <KEY> | <INFO> +
    # + ...            +
    # + <KEY> | <INFO> +
    # +----------------+
    #
    @staticmethod
    def _build_gamecart_info_components() -> List[sg.Element]:
        """Build game cart info components."""
        column_layout = [
            [
                MainLayoutBuilder._build_info_key_text(field, key=field_key),
                MainLayoutBuilder._build_info_value_text(
                    wrap_text(
                        MainLayoutBuilder.default_game_cart_box_info_value_text(),
                        VALUE_TEXT_WIDTH,
                        VALUE_TEXT_MAX_LINES_PER_KEY[value_key],
                    ),
                    key=value_key,
                ),
            ]
            for field, field_key, value_key in [
                (
                    "Name",
                    ComponentKey.GAME_CART_BOX_FIELD_NAME,
                    ComponentKey.GAME_CART_BOX_VALUE_NAME,
                ),
                (
                    "Description",
                    ComponentKey.GAME_CART_BOX_FIELD_DESCRIPTION,
                    ComponentKey.GAME_CART_BOX_VALUE_DESCRIPTION,
                ),
                (
                    "Platform",
                    ComponentKey.GAME_CART_BOX_FIELD_PLATFORM,
                    ComponentKey.GAME_CART_BOX_VALUE_PLATFORM,
                ),
                (
                    "Genre",
                    ComponentKey.GAME_CART_BOX_FIELD_GENRE,
                    ComponentKey.GAME_CART_BOX_VALUE_GENRE,
                ),
                (
                    "Developer",
                    ComponentKey.GAME_CART_BOX_FIELD_DEVELOPER,
                    ComponentKey.GAME_CART_BOX_VALUE_DEVELOPER,
                ),
                (
                    "Region",
                    ComponentKey.GAME_CART_BOX_FIELD_REGION,
                    ComponentKey.GAME_CART_BOX_VALUE_REGION,
                ),
                (
                    "Release",
                    ComponentKey.GAME_CART_BOX_FIELD_RELEASE,
                    ComponentKey.GAME_CART_BOX_VALUE_RELEASE,
                ),
            ]
        ]
        column_layout[0].append(sg.Push())
        return FrameBuilder.build(
            "Information",
            [[sg.Column(column_layout)]],
        ).set_expand_y()

    @staticmethod
    def _build_info_key_text(text: str, key: str) -> sg.Text:
        """Build text key."""
        return sg.vtop(
            TextBuilder.build(text, key=key).set_upper().set_size((KEY_TEXT_WIDTH, 1)).set_font("bold"),
        )

    @staticmethod
    def _build_info_value_text(text: str, key: str) -> sg.Text:
        """Build text value."""
        return sg.vcenter(
            TextBuilder.build(text, key=key).set_font(
                ("Consolas", 14) if os.name == 'nt' else ("Andale Mono", 12),
            ),  # use monospace font to prevent window from auto-resizing
        )
