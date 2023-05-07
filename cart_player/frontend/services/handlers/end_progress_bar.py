from typing import Type

from cart_player.core import Broker, Handler
from cart_player.frontend.domain.commands import EndProgressBarCommand
from cart_player.frontend.domain.ports import App


class EndProgressBarHandler(Handler):
    """Handle event 'EndProgressBarCommand'."""

    def __init__(self, broker: Broker, app: App):
        super().__init__(broker)
        self._app = app

    @property
    def message_type(self) -> Type:
        return EndProgressBarCommand

    def _handle(self, evt: EndProgressBarCommand):
        self._app.complete_progress_bar(failure=evt.failure)
