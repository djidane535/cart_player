from typing import Type

from cart_player.backend.adapters.memory import LocalMemory
from cart_player.backend.domain.commands import UpdateLocalMemoryConfigurationCommand
from cart_player.backend.domain.events import LocalMemoryConfigurationUpdatedEvent
from cart_player.core import Broker, Handler


class UpdateLocalMemoryConfigurationHandler(Handler):
    """Handle event 'UpdateLocalMemoryConfigurationCommand'."""

    def __init__(self, broker: Broker, local_memory: LocalMemory):
        super().__init__(broker)
        self._local_memory = local_memory

    @property
    def message_type(self) -> Type:
        return UpdateLocalMemoryConfigurationCommand

    def _handle(self, cmd: UpdateLocalMemoryConfigurationCommand):
        self._local_memory.update_configuration(cmd)
        self._publish(
            LocalMemoryConfigurationUpdatedEvent(new_memory_configuration=cmd),
        )
