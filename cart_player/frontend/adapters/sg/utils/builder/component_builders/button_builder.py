import base64
import os

import PySimpleGUI as sg

from cart_player.frontend.adapters.sg.utils.image import invert_colors
from cart_player.frontend.resources.image import button_border_filepath

from .component_key import ComponentKey
from .focusable import Focusable
from .freezable import Freezable


class ButtonBuilder:
    @staticmethod
    def build(
        name: str,
        tooltip: str,
        key: ComponentKey,
        dangerous_button: bool = False,
        disabled: bool = False,
        image_filepath: str = None,
    ) -> sg.Button:
        """Build a button."""
        return Button(
            button_text=name,
            button_text_color="red" if dangerous_button else None,
            image_filepath=image_filepath,
            font_size=14 if os.name == 'nt' else 16,
            tooltip=tooltip,
            disabled=disabled,
            key=key,
        )

    @staticmethod
    def build_layout_selector_button(
        name: str,
        tooltip: str,
        key: ComponentKey,
    ) -> sg.Button:
        """Build a button."""
        return Button(
            button_text=name,
            font_size=20 if os.name == 'nt' else 24,
            borderless=True,
            tooltip=tooltip,
            key=key,
        )

    @staticmethod
    def build_generic_warning_close_button(close_button_name: str) -> sg.Button:
        """Build a button."""
        return sg.Button(close_button_name, button_color=("white", "orange"))

    @staticmethod
    def build_generic_error_close_button(close_button_name: str) -> sg.Button:
        """Build a button."""
        return sg.Button(close_button_name, button_color=("white", "red"))


class Button(sg.Button, Focusable, Freezable):
    def __init__(
        self,
        tooltip: str,
        key: ComponentKey,
        button_text: str = "",
        button_text_color: str = None,
        image_filepath: str = None,
        font_size: int = 14 if os.name == 'nt' else 16,
        borderless: bool = False,
        disabled: bool = False,
    ):
        self._init_button_text_color = button_text_color
        image_filepath = image_filepath or (button_border_filepath if not borderless else None)
        image_data = None
        inverted_image_data = None
        if image_filepath:
            with open(image_filepath, "rb") as image_file:
                image_data = base64.b64encode(image_file.read())
                inverted_image_data = invert_colors(image_data)

        sg.Button.__init__(
            self,
            button_text=button_text,
            image_data=image_data if not image_data or not disabled else inverted_image_data,
            font=("Arial", f"{font_size}") if not borderless else ("Arial", f"{font_size}", "bold"),
            button_color=self._get_button_color(disabled),
            mouseover_colors=("#FFFFBB", sg.theme_background_color()),
            border_width=0,
            tooltip=tooltip,
            disabled=disabled,
            key=key,
        )
        self._image_data: bytes = image_data
        self._inverted_image_data: bytes = inverted_image_data

    def disable_focus(self):
        self.Widget.config(takefocus=0)

    def enable_focus(self):
        self.Widget.config(takefocus=1)

    def freeze(self):
        self.update(disabled=True)
        self.update(button_color=self._get_button_color(True), image_data=self._inverted_image_data)

    def unfreeze(self):
        self.update(disabled=False)
        self.update(button_color=self._get_button_color(False), image_data=self._image_data)

    def _get_button_color(self, disabled: bool) -> tuple:
        if disabled:
            return sg.theme_background_color()
        return (
            self._init_button_text_color if self._init_button_text_color else sg.theme_text_color(),
            sg.theme_background_color(),
        )
