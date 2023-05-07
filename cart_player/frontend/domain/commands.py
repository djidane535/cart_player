from datetime import timedelta
from typing import Optional

from pydantic import ValidationError, validator

from cart_player.core.domain.messages import BaseMessage


class BeginProgressBarCommand(BaseMessage):
    pass


class ClosePopUpWindow(BaseMessage):
    pass


class EndProgressBarCommand(BaseMessage):
    failure: bool = False


class OpenPlayWindowCommand(BaseMessage):
    pass


class OpenDataWindowCommand(BaseMessage):
    pass


class OpenSettingsWindowCommand(BaseMessage):
    pass


class OpenPopUpWarningWindowCommand(BaseMessage):
    message: str

    @validator("message")
    def message_is_not_empty(cls, v):
        if not v:
            raise ValidationError("Message is missing.")
        return v


class OpenPopUpErrorWindowCommand(OpenPopUpWarningWindowCommand):
    close_app: bool


class RestorePreviousWindowCommand(BaseMessage):
    pass


class StopAppCommand(BaseMessage):
    pass


class UpdateProgressBarCommand(BaseMessage):
    value: int

    @validator("value")
    def value_is_in_range(cls, v):
        if v < 0 or v > 100:
            raise ValidationError(f"Value must be in [0, 100] (got: {v}).")
        return v


class UpdateETACommand(BaseMessage):
    eta: Optional[timedelta]
