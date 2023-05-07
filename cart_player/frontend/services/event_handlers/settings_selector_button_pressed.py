from typing import Type

from cart_player.core import Handler
from cart_player.frontend.domain.commands import OpenSettingsWindowCommand
from cart_player.frontend.domain.events import SettingsSelectorButtonPressedEvent


class SettingsSelectorButtonPressedEventHandler(Handler):
    """Handle event 'SettingsSelectorButtonPressedEvent'."""

    @property
    def message_type(self) -> Type:
        return SettingsSelectorButtonPressedEvent

    def _handle(self, evt: SettingsSelectorButtonPressedEvent):
        self._publish(OpenSettingsWindowCommand())
