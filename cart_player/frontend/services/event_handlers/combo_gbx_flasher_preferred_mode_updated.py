from typing import Type

from cart_player.backend.api.commands import UpdateGBXFlasherConfigurationCommand
from cart_player.core import Handler
from cart_player.frontend.domain.events import ComboGBXFlasherPreferredModeUpdated


class ComboGBXFlasherPreferredModeUpdatedHandler(Handler):
    """Handle event 'ComboGBXFlasherPreferredModeUpdated'."""

    @property
    def message_type(self) -> Type:
        return ComboGBXFlasherPreferredModeUpdated

    def _handle(self, evt: ComboGBXFlasherPreferredModeUpdated):
        self._publish(UpdateGBXFlasherConfigurationCommand(preferred_mode=evt.mode))
