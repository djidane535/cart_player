from typing import Type

from cart_player.backend.api.events import GBXFlasherConfigurationUpdatedEvent
from cart_player.core import Broker, Handler

from ....settings import SETTINGS_FLASHER_PREFERRED_MODE, settings


class GBXFlasherConfigurationUpdatedEventHandler(Handler):
    """Handle event 'GBXFlasherConfigurationUpdatedEvent'."""

    def __init__(self, broker: Broker):
        super().__init__(broker)

    @property
    def message_type(self) -> Type:
        return GBXFlasherConfigurationUpdatedEvent

    def _handle(self, evt: GBXFlasherConfigurationUpdatedEvent):
        settings.set(SETTINGS_FLASHER_PREFERRED_MODE, evt.new_flasher_configuration.preferred_mode.value)
        settings.save()
