from typing import Type

from cart_player.backend.domain.commands import SetupGameFileAndSaveFileForPlayingCommand
from cart_player.core import Broker, Handler
from cart_player.frontend.domain.events import LaunchButtonPressedEvent
from cart_player.frontend.domain.ports import App


class LaunchButtonPressedEventHandler(Handler):
    """Handle event 'LaunchButtonPressedEvent'."""

    def __init__(self, broker: Broker, app: App):
        super().__init__(broker)
        self._app = app

    @property
    def message_type(self) -> Type:
        return LaunchButtonPressedEvent

    def _handle(self, evt: LaunchButtonPressedEvent):
        self._app.start_game_session()
        self._publish(
            SetupGameFileAndSaveFileForPlayingCommand(
                game_name=evt.game_name, save_name=evt.save_name, target_path=evt.game_session_path
            )
        )
