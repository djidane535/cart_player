from typing import Type

from cart_player.backend.api.commands import EraseCartSaveCommand
from cart_player.core import Handler
from cart_player.frontend.domain.commands import BeginProgressBarCommand
from cart_player.frontend.domain.events import EraseButtonPressedEvent


class EraseButtonPressedEventHandler(Handler):
    """Handle event 'EraseButtonPressedEvent'."""

    @property
    def message_type(self) -> Type:
        return EraseButtonPressedEvent

    def _handle(self, evt: EraseButtonPressedEvent):
        self._publish(BeginProgressBarCommand())
        self._publish(EraseCartSaveCommand())
