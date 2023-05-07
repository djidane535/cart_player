from typing import Type

from cart_player.backend.api.commands import ReadCartDataCommand
from cart_player.backend.api.events import CartSaveErasedEvent
from cart_player.core import Broker, Handler
from cart_player.frontend.domain.commands import EndProgressBarCommand


class CartSaveErasedEventHandler(Handler):
    """Handle event 'CartSaveErasedEvent'."""

    def __init__(self, broker: Broker):
        super().__init__(broker)

    @property
    def message_type(self) -> Type:
        return CartSaveErasedEvent

    def _handle(self, evt: CartSaveErasedEvent):
        if evt.success:
            self._publish(EndProgressBarCommand())
            self._publish(
                ReadCartDataCommand(
                    cart_info=evt.cart_info,
                    skip_game_metadata=True,
                    skip_game_image=True,
                ),
            )
        else:
            self._publish(EndProgressBarCommand(failure=True))
