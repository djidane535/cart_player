from typing import Type

from cart_player.backend.api.commands import BackupCartSaveCommand
from cart_player.core import Handler
from cart_player.frontend.domain.commands import BeginProgressBarCommand
from cart_player.frontend.domain.events import BackupButtonPressedEvent


class BackupButtonPressedEventHandler(Handler):
    """Handle event 'BackupButtonPressedEvent'."""

    @property
    def message_type(self) -> Type:
        return BackupButtonPressedEvent

    def _handle(self, evt: BackupButtonPressedEvent):
        self._publish(BeginProgressBarCommand())
        self._publish(BackupCartSaveCommand())
