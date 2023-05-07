from typing import Type

from cart_player.core import Broker, Handler
from cart_player.frontend.domain.commands import StopAppCommand
from cart_player.frontend.domain.ports import App


class StopAppHandler(Handler):
    """Handle event 'StopAppCommand'."""

    def __init__(self, broker: Broker, app: App):
        super().__init__(broker)
        self._app = app

    @property
    def message_type(self) -> Type:
        return StopAppCommand

    def _handle(self, evt: StopAppCommand):
        self._app.stop()
