from __future__ import annotations

import PySimpleGUI as sg


class FrameBuilder:
    @staticmethod
    def build(title: str, layout) -> Frame:
        return Frame(title, layout)


class Frame(sg.Frame):
    def set_expand_x(self, v: bool = True) -> Frame:
        self.expand_x = True
        return self

    def set_expand_y(self, v: bool = True) -> Frame:
        self.expand_y = True
        return self
