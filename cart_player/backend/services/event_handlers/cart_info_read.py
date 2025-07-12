from typing import Type

from cart_player.backend.api.events import CartDataReadEvent
from cart_player.backend.domain.commands import ExportToAnaloguePocketLibraryCommand
from cart_player.core import Broker, Handler


class CartDataReadEventHandler(Handler):
    """Handle event 'CartDataReadEvent'."""

    def __init__(self, broker: Broker):
        super().__init__(broker)

    @property
    def message_type(self) -> Type:
        return CartDataReadEvent

    def _handle(self, evt: CartDataReadEvent):
        if (
            # cart_info
            not evt.cart_info or evt.cart_info.is_empty or
            # game_metadata
            not evt.game_metadata or not evt.game_metadata.crc or
            # game_image
            not evt.game_image or not evt.game_image.data
        ):
            return

        self._publish(
            ExportToAnaloguePocketLibraryCommand(
                cart_info=evt.cart_info, 
                game_image=evt.game_image, 
                game_metadata=evt.game_metadata
            )
        )
