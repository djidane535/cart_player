from __future__ import annotations

from typing import Tuple, Union

import FreeSimpleGUI as sg


class TextBuilder:
    @staticmethod
    def build(
        content: str,
        editable: bool = False,
        key: str = None,
        right_click_edit: bool = False,
        right_click_clear: bool = False,
    ) -> Union[Text, InputText]:
        click_menu_items = []
        if right_click_edit:
            click_menu_items.append(f"Edit::{key}")
        if right_click_clear:
            click_menu_items.append(f"Clear::{key}")
        right_click_menu = None if not len(click_menu_items) else ["", click_menu_items]

        return (
            Text(content, key=key, right_click_menu=right_click_menu)
            if not editable
            else InputText(content, key=key, right_click_menu=right_click_menu)
        )


class BaseText:
    def set_upper(self) -> Text:
        self.DisplayText = self.DisplayText.upper()
        return self

    def set_size(self, size: Tuple[int, int]) -> Text:
        self.Size = size
        return self

    def set_font(self, font: str) -> Text:
        self.Font = font
        return self

    def set_color(self, color: str) -> Text:
        self.TextColor = color
        return self


class Text(BaseText, sg.Text):
    pass


class InputText(BaseText, sg.InputText):
    pass
