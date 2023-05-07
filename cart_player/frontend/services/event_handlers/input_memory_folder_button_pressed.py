from pathlib import Path
from typing import Type

from cart_player.backend.api.commands import UpdateLocalMemoryConfigurationCommand
from cart_player.core import Handler
from cart_player.frontend.domain.events import InputMemoryFolderButtonPressedEvent


class InputMemoryFolderButtonPressedEventHandler(Handler):
    """Handle event 'InputMemoryFolderButtonPressedEvent'."""

    @property
    def message_type(self) -> Type:
        return InputMemoryFolderButtonPressedEvent

    def _handle(self, evt: InputMemoryFolderButtonPressedEvent):
        path: Path = Path(evt.path_str)
        self._publish(UpdateLocalMemoryConfigurationCommand(root_path=path))
