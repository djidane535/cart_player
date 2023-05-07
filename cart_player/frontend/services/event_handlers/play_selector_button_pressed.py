from typing import Type

from cart_player.core import Handler
from cart_player.frontend.domain.commands import OpenPlayWindowCommand
from cart_player.frontend.domain.events import PlaySelectorButtonPressedEvent


class PlaySelectorButtonPressedEventHandler(Handler):
    """Handle event 'PlaySelectorButtonPressedEvent'."""

    @property
    def message_type(self) -> Type:
        return PlaySelectorButtonPressedEvent

    def _handle(self, evt: PlaySelectorButtonPressedEvent):
        self._publish(OpenPlayWindowCommand())
