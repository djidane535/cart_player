from typing import Type

from cart_player.core import Broker, Handler
from cart_player.frontend.domain.commands import RestorePreviousWindowCommand
from cart_player.frontend.domain.ports import App


class RestorePreviousWindowHandler(Handler):
    """Handle event 'RestorePreviousWindowCommand'."""

    def __init__(self, broker: Broker, app: App):
        super().__init__(broker)
        self._app = app

    @property
    def message_type(self) -> Type:
        return RestorePreviousWindowCommand

    def _handle(self, evt: RestorePreviousWindowCommand):
        self._app.end_game_session()
        self._app.restore_previous_window()
