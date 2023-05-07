from typing import Type

from cart_player.core import Handler
from cart_player.frontend.domain.commands import StopAppCommand
from cart_player.frontend.domain.events import WindowCloseAttemptedEvent


class WindowCloseAttemptedEventHandler(Handler):
    """Handle event 'WindowCloseAttemptedEvent'."""

    @property
    def message_type(self) -> Type:
        return WindowCloseAttemptedEvent

    def _handle(self, evt: WindowCloseAttemptedEvent):
        self._publish(StopAppCommand())
