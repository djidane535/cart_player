from __future__ import annotations

from typing import Tuple

import FreeSimpleGUI as sg


class MultilineBuilder:
    """note: always editable"""
    @staticmethod
    def build(content: str, editable: bool = False, size: Tuple[int, int] = None, key: str = None) -> Multiline:
        return Multiline(content, key=key, disabled=not editable, expand_y=True, size=size)

class Multiline(sg.Multiline):
    pass
