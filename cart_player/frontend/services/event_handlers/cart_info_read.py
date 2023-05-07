from typing import Type

from cart_player.backend.api.dtos import CartInfo, GameImage, GameMetadata
from cart_player.backend.api.events import CartDataReadEvent
from cart_player.core import Broker, Handler
from cart_player.frontend.domain.ports import App


class CartDataReadEventHandler(Handler):
    """Handle event 'CartDataReadEvent'."""

    def __init__(self, broker: Broker, app: App):
        super().__init__(broker)
        self._app = app

    @property
    def message_type(self) -> Type:
        return CartDataReadEvent

    def _handle(self, evt: CartDataReadEvent):
        # App update
        self._app.updating_cart_data()
        if evt.success:
            self._app.update_cart_data(
                evt.cart_info,
                evt.game_data_list,
                evt.game_metadata,
                evt.game_image,
            )
        else:
            self._app.update_cart_data(CartInfo(), [], GameMetadata(), GameImage())
