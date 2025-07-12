from typing import Type

from cart_player.backend.api.commands import ReadCartDataCommand
from cart_player.backend.api.events import GameDataDeletedEvent
from cart_player.core import Broker, Handler


class GameDataDeletedEventHandler(Handler):
    """Handle event 'GameDataDeletedEvent'."""

    def __init__(self, broker: Broker):
        super().__init__(broker)

    @property
    def message_type(self) -> Type:
        return GameDataDeletedEvent

    def _handle(self, evt: GameDataDeletedEvent):
        self._publish(ReadCartDataCommand(cart_info=evt.cart_info))
