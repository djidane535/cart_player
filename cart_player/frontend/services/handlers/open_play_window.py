from typing import Type

from cart_player.core import Broker, Handler
from cart_player.frontend.domain.commands import OpenPlayWindowCommand
from cart_player.frontend.domain.ports import App


class OpenPlayWindowHandler(Handler):
    """Handle event 'OpenPlayWindowCommand'."""

    def __init__(self, broker: Broker, app: App):
        super().__init__(broker)
        self._app = app

    @property
    def message_type(self) -> Type:
        return OpenPlayWindowCommand

    def _handle(self, evt: OpenPlayWindowCommand):
        self._app.open_play_window()
