from typing import Type

from cart_player.core import Broker, Handler
from cart_player.frontend.domain.commands import OpenSettingsWindowCommand
from cart_player.frontend.domain.ports import App


class OpenSettingsWindowHandler(Handler):
    """Handle event 'OpenSettingsWindowCommand'."""

    def __init__(self, broker: Broker, app: App):
        super().__init__(broker)
        self._app = app

    @property
    def message_type(self) -> Type:
        return OpenSettingsWindowCommand

    def _handle(self, evt: OpenSettingsWindowCommand):
        self._app.open_settings_window()
