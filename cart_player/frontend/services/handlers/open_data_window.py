from typing import Type

from cart_player.core import Broker, Handler
from cart_player.frontend.domain.commands import OpenDataWindowCommand
from cart_player.frontend.domain.ports import App


class OpenDataWindowHandler(Handler):
    """Handle event 'OpenDataWindowCommand'."""

    def __init__(self, broker: Broker, app: App):
        super().__init__(broker)
        self._app = app

    @property
    def message_type(self) -> Type:
        return OpenDataWindowCommand

    def _handle(self, evt: OpenDataWindowCommand):
        self._app.open_data_window()
