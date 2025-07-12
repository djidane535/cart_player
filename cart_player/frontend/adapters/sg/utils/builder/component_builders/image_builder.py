from __future__ import annotations

import base64

import FreeSimpleGUI as sg

from cart_player.frontend.adapters.sg.utils.image import put_image_into_square


class ImageBuilder:
    @staticmethod
    def build(
        filepath: str,
        square_size: int = None,
        key: str = None,
        right_click_edit: bool = False,
        right_click_clear: bool = False,
    ) -> sg.Image:
        """Build image."""
        if square_size is None:
            return sg.Image(filepath, pad=(15, 15), key=key)

        with open(filepath, "rb") as f:
            data = base64.b64encode(f.read())

        squared_image_data = put_image_into_square(data, square_size)
        click_menu_items = []
        if right_click_edit:
            click_menu_items.append(f"Edit::{key}")
        if right_click_clear:
            click_menu_items.append(f"Clear::{key}")
        right_click_menu = None if not len(click_menu_items) else ["", click_menu_items]

        return sg.Image(
            data=squared_image_data, pad=(15, 15), key=key, right_click_menu=right_click_menu
        )
