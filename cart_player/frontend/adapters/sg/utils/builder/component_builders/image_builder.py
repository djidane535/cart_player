from __future__ import annotations

import base64

import PySimpleGUI as sg

from cart_player.frontend.adapters.sg.utils.image import put_image_into_square


class ImageBuilder:
    @staticmethod
    def build(filepath: str, square_size: int = None, key: str = None) -> sg.Image:
        """Build image."""
        if square_size is None:
            return sg.Image(filepath, pad=(15, 15), key=key)

        with open(filepath, "rb") as f:
            data = base64.b64encode(f.read())

        squared_image_data = put_image_into_square(data, square_size)
        return sg.Image(data=squared_image_data, pad=(15, 15), key=key)
