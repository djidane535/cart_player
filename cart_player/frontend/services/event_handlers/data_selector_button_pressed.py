from typing import Type

from cart_player.core import Handler
from cart_player.frontend.domain.commands import OpenDataWindowCommand
from cart_player.frontend.domain.events import DataSelectorButtonPressedEvent


class DataSelectorButtonPressedEventHandler(Handler):
    """Handle event 'DataSelectorButtonPressedEvent'."""

    @property
    def message_type(self) -> Type:
        return DataSelectorButtonPressedEvent

    def _handle(self, evt: DataSelectorButtonPressedEvent):
        self._publish(OpenDataWindowCommand())
