from typing import Type

from cart_player.backend.api.events import WriteCartSaveProgressEvent
from cart_player.core import Handler
from cart_player.frontend.domain.commands import UpdateETACommand, UpdateProgressBarCommand


class WriteCartSaveProgressEventHandler(Handler):
    """Handle event 'WriteCartSaveProgressEvent'."""

    @property
    def message_type(self) -> Type:
        return WriteCartSaveProgressEvent

    def _handle(self, evt: WriteCartSaveProgressEvent):
        self._publish(UpdateProgressBarCommand(value=evt.percent))
        self._publish(UpdateETACommand(eta=evt.eta))
