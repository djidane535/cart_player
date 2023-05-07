from typing import Type

from cart_player.backend.api.commands import ReadCartDataCommand
from cart_player.core import Broker, Handler
from cart_player.frontend.domain.events import RefreshButtonPressedEvent
from cart_player.frontend.domain.ports import App


class RefreshButtonPressedEventHandler(Handler):
    """Handle event 'RefreshButtonPressedEvent'."""

    def __init__(self, broker: Broker, app: App):
        super().__init__(broker)
        self._app = app

    @property
    def message_type(self) -> Type:
        return RefreshButtonPressedEvent

    def _handle(self, evt: RefreshButtonPressedEvent):
        self._app.freeze()
        self._publish(ReadCartDataCommand(raise_error=False))
