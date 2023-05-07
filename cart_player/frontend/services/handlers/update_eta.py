from typing import Type

from cart_player.core import Broker, Handler
from cart_player.frontend.domain.commands import UpdateETACommand
from cart_player.frontend.domain.ports import App


class UpdateETAHandler(Handler):
    """Handle event 'UpdateETACommand'."""

    def __init__(self, broker: Broker, app: App):
        super().__init__(broker)
        self._app = app

    @property
    def message_type(self) -> Type:
        return UpdateETACommand

    def _handle(self, evt: UpdateETACommand):
        self._app.update_eta(evt.eta)
