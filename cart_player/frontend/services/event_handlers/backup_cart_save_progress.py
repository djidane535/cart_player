from typing import Type

from cart_player.backend.api.events import BackupCartSaveProgressEvent
from cart_player.core import Handler
from cart_player.frontend.domain.commands import UpdateETACommand, UpdateProgressBarCommand


class BackupCartSaveProgressEventHandler(Handler):
    """Handle event 'BackupCartSaveProgressEvent'."""

    @property
    def message_type(self) -> Type:
        return BackupCartSaveProgressEvent

    def _handle(self, evt: BackupCartSaveProgressEvent):
        self._publish(UpdateProgressBarCommand(value=evt.percent))
        self._publish(UpdateETACommand(eta=evt.eta))
