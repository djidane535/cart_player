from typing import Type

from cart_player.backend.api.events import LocalMemoryConfigurationUpdatedEvent
from cart_player.core import Broker, Handler

from ....settings import SETTINGS_MEMORY_PATH, settings


class LocalMemoryConfigurationUpdatedEventHandler(Handler):
    """Handle event 'LocalMemoryConfigurationUpdatedEvent'."""

    def __init__(self, broker: Broker):
        super().__init__(broker)

    @property
    def message_type(self) -> Type:
        return LocalMemoryConfigurationUpdatedEvent

    def _handle(self, evt: LocalMemoryConfigurationUpdatedEvent):
        settings.set(SETTINGS_MEMORY_PATH, str(evt.new_memory_configuration.root_path))
        settings.save()
