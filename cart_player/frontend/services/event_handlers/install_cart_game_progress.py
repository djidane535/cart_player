from typing import Type

from cart_player.backend.api.events import InstallCartGameProgressEvent
from cart_player.core import Handler
from cart_player.frontend.domain.commands import UpdateETACommand, UpdateProgressBarCommand


class InstallCartGameProgressEventHandler(Handler):
    """Handle event 'InstallCartGameProgressEvent'."""

    @property
    def message_type(self) -> Type:
        return InstallCartGameProgressEvent

    def _handle(self, evt: InstallCartGameProgressEvent):
        self._publish(UpdateProgressBarCommand(value=evt.percent))
        self._publish(UpdateETACommand(eta=evt.eta))
