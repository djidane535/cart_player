import traceback
from datetime import timedelta
from typing import Optional

from pydantic import ValidationError, validator

from .messages import BaseMessage


class ProgressEvent(BaseMessage):
    current: float
    total: float = 1.0
    eta: Optional[timedelta]

    @property
    def percent(self) -> int:
        """Progress in percent."""
        return min(max(0, round((self.current / self.total) * 100)), 100)


class UnexpectedWarningEvent(BaseMessage):
    message: str
    trace: str

    @validator("message")
    def message_is_not_empty(cls, v):
        if not v:
            raise ValidationError("Message is missing.")
        return v


class UnexpectedErrorEvent(UnexpectedWarningEvent):
    close_app: bool
