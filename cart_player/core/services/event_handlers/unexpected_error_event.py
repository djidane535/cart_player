from typing import Type

from cart_player.core import Handler
from cart_player.core.domain.events import UnexpectedErrorEvent
from cart_player.frontend.domain.commands import OpenPopUpErrorWindowCommand


class UnexpectedErrorEventHandler(Handler):
    """Handle event 'UnexpectedErrorEvent'."""

    @property
    def message_type(self) -> Type:
        return UnexpectedErrorEvent

    def _handle(self, evt: UnexpectedErrorEvent):
        self._publish(OpenPopUpErrorWindowCommand(message=evt.message, close_app=evt.close_app))
