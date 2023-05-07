from typing import Type

from cart_player.core import Broker, Handler
from cart_player.core.utils import open_folder
from cart_player.frontend.domain.commands import OpenPopUpErrorWindowCommand
from cart_player.frontend.domain.ports import App
from cart_player.logging_handlers import LOG_DIRECTORY


class OpenPopUpErrorWindowHandler(Handler):
    """Handle event 'OpenPopUpErrorWindowCommand'."""

    def __init__(self, broker: Broker, app: App):
        super().__init__(broker)
        self._app = app

    @property
    def message_type(self) -> Type:
        return OpenPopUpErrorWindowCommand

    def _handle(self, evt: OpenPopUpErrorWindowCommand):
        self._app.open_pop_up_error_window(evt.message, evt.close_app)
        if evt.close_app:
            open_folder(LOG_DIRECTORY)
