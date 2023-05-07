from typing import Type

from cart_player.core import Handler
from cart_player.core.domain.events import UnexpectedWarningEvent
from cart_player.frontend.domain.commands import OpenPopUpWarningWindowCommand


class UnexpectedWarningEventHandler(Handler):
    """Handle event 'UnexpectedWarningEvent'."""

    @property
    def message_type(self) -> Type:
        return UnexpectedWarningEvent

    def _handle(self, evt: UnexpectedWarningEvent):
        self._publish(OpenPopUpWarningWindowCommand(message=evt.message))
