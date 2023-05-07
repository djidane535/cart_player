from typing import Type

from cart_player.backend.api.commands import InstallCartGameCommand
from cart_player.core import Handler
from cart_player.frontend.domain.commands import BeginProgressBarCommand
from cart_player.frontend.domain.events import InstallButtonPressedEvent


class InstallButtonPressedEventHandler(Handler):
    """Handle event 'InstallButtonPressedEvent'."""

    @property
    def message_type(self) -> Type:
        return InstallButtonPressedEvent

    def _handle(self, evt: InstallButtonPressedEvent):
        self._publish(BeginProgressBarCommand())
        self._publish(InstallCartGameCommand())
