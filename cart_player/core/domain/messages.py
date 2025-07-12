from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class BaseMessage(BaseModel):
    def __str__(self):
        return f"{self.__class__.__name__}({super().__str__()})"
