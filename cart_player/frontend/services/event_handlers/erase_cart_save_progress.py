from typing import Type

from cart_player.backend.api.events import EraseCartSaveProgressEvent
from cart_player.core import Handler
from cart_player.frontend.domain.commands import UpdateETACommand, UpdateProgressBarCommand


class EraseCartSaveProgressEventHandler(Handler):
    """Handle event 'EraseCartSaveProgressEvent'."""

    @property
    def message_type(self) -> Type:
        return EraseCartSaveProgressEvent

    def _handle(self, evt: EraseCartSaveProgressEvent):
        self._publish(UpdateProgressBarCommand(value=evt.percent))
        self._publish(UpdateETACommand(eta=evt.eta))
