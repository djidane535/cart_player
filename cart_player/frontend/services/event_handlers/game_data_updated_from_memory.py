from typing import Type

from cart_player.backend.api.commands import ReadCartDataCommand
from cart_player.backend.api.events import GameDataUpdatedEvent
from cart_player.core import Broker, Handler
from cart_player.frontend.domain.commands import RestorePreviousWindowCommand


class GameDataUpdatedEventHandler(Handler):
    """Handle event 'GameDataUpdatedEvent'."""

    def __init__(self, broker: Broker):
        super().__init__(broker)

    @property
    def message_type(self) -> Type:
        return GameDataUpdatedEvent

    def _handle(self, evt: GameDataUpdatedEvent):
        self._publish(
            RestorePreviousWindowCommand(
                on_end_emit=ReadCartDataCommand(cart_info=evt.cart_info, raise_error=False)
            )
        )
