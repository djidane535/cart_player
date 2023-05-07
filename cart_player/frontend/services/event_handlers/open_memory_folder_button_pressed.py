import os
from typing import Type

from cart_player.core import Handler
from cart_player.frontend.domain.events import OpenMemoryButtonPressedEvent


class OpenMemoryButtonPressedEventHandler(Handler):
    """Handle event 'OpenMemoryButtonPressedEvent'."""

    @property
    def message_type(self) -> Type:
        return OpenMemoryButtonPressedEvent

    def _handle(self, evt: OpenMemoryButtonPressedEvent):
        # Open folder
        if os.name == 'nt':  # for Windows
            os.startfile(evt.memory_path)
        elif os.name == 'posix':  # for macOS and Linux
            os.system('open "{}"'.format(evt.memory_path))
        else:
            raise RuntimeError("Unsupported operating system")
