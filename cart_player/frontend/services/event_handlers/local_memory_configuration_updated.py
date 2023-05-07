from typing import Type

from cart_player.backend.api.commands import ReadCartDataCommand
from cart_player.backend.api.events import LocalMemoryConfigurationUpdatedEvent
from cart_player.core import Broker, Handler
from cart_player.frontend.domain.ports import App, LocalMemoryConfigurable


class LocalMemoryConfigurationUpdatedEventHandler(Handler):
    """Handle event 'LocalMemoryConfigurationUpdatedEvent'."""

    def __init__(self, broker: Broker, app: App):
        super().__init__(broker)
        self._app = app

    @property
    def message_type(self) -> Type:
        return LocalMemoryConfigurationUpdatedEvent

    def _handle(self, evt: LocalMemoryConfigurationUpdatedEvent):
        if isinstance(self._app, LocalMemoryConfigurable):
            self._app.update_local_memory_config(evt.new_memory_configuration)
            self._publish(ReadCartDataCommand(raise_error=False))
