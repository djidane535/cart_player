from typing import Type

from cart_player.backend.api.commands import WriteCartSaveCommand
from cart_player.core import Handler
from cart_player.frontend.domain.commands import BeginProgressBarCommand
from cart_player.frontend.domain.events import UploadButtonPressedEvent


class UploadButtonPressedEventHandler(Handler):
    """Handle event 'UploadButtonPressedEvent'."""

    @property
    def message_type(self) -> Type:
        return UploadButtonPressedEvent

    def _handle(self, evt: UploadButtonPressedEvent):
        self._publish(BeginProgressBarCommand())
        self._publish(WriteCartSaveCommand(save_name=evt.save_name))
