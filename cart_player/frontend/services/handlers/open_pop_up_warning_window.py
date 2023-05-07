from typing import Type

from cart_player.core import Broker, Handler
from cart_player.frontend.domain.commands import OpenPopUpWarningWindowCommand
from cart_player.frontend.domain.ports import App


class OpenPopUpWarningWindowHandler(Handler):
    """Handle event 'OpenPopUpWarningWindowCommand'."""

    def __init__(self, broker: Broker, app: App):
        super().__init__(broker)
        self._app = app

    @property
    def message_type(self) -> Type:
        return OpenPopUpWarningWindowCommand

    def _handle(self, evt: OpenPopUpWarningWindowCommand):
        self._app.open_pop_up_warning_window(evt.message)
