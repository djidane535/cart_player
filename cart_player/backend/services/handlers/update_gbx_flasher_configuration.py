from typing import Type

from cart_player.backend.adapters.cart_flasher import GBXFlasher
from cart_player.backend.domain.commands import UpdateGBXFlasherConfigurationCommand
from cart_player.backend.domain.events import GBXFlasherConfigurationUpdatedEvent
from cart_player.core import Broker, Handler


class UpdateGBXFLasherConfigurationHandler(Handler):
    """Handle event 'UpdateLocalMemoryConfigurationCommand'."""

    def __init__(self, broker: Broker, gbx_flasher: GBXFlasher):
        super().__init__(broker)
        self._gbx_flasher = gbx_flasher

    @property
    def message_type(self) -> Type:
        return UpdateGBXFlasherConfigurationCommand

    def _handle(self, cmd: UpdateGBXFlasherConfigurationCommand):
        self._gbx_flasher.update_configuration(cmd)
        self._publish(
            GBXFlasherConfigurationUpdatedEvent(new_flasher_configuration=cmd),
        )