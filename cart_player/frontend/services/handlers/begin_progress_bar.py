from typing import Type

from cart_player.core import Broker, Handler
from cart_player.frontend.domain.commands import BeginProgressBarCommand
from cart_player.frontend.domain.ports import App


class BeginProgressBarHandler(Handler):
    """Handle event 'BeginProgressBarCommand'."""

    def __init__(self, broker: Broker, app: App):
        super().__init__(broker)
        self._app = app

    @property
    def message_type(self) -> Type:
        return BeginProgressBarCommand

    def _handle(self, evt: BeginProgressBarCommand):
        self._app.reset_progress_bar()
        self._app.freeze()
