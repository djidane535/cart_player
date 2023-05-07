from __future__ import annotations

from typing import Tuple, Union

import PySimpleGUI as sg


class TextBuilder:
    @staticmethod
    def build(content: str, editable: bool = False, key: str = None) -> Union[Text, InputText]:
        return Text(content, key=key) if not editable else InputText(content, key=key)


class BaseText(sg.Element):
    def __init__(self, text: str, key: str):
        super().__init__(text, key=key)

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
