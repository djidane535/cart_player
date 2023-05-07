from typing import Type

from cart_player.backend.domain.commands import BackupSaveFileAfterPlayingCommand, ReadCartDataCommand
from cart_player.core import Handler
from cart_player.frontend.domain.commands import RestorePreviousWindowCommand
from cart_player.frontend.domain.events import PopUpWindowIsClosingEvent


class PopUpWindowIsClosingEventHandler(Handler):
    """Handle event 'PopUpWindowIsClosingEvent'."""

    @property
    def message_type(self) -> Type:
        return PopUpWindowIsClosingEvent

    def _handle(self, evt: PopUpWindowIsClosingEvent):
        if evt.play_window_is_closing and evt.cart_info:
            self._publish(BackupSaveFileAfterPlayingCommand(cart_info=evt.cart_info, target_path=evt.game_session_path))
            self._publish(ReadCartDataCommand(raise_error=False))
        self._publish(RestorePreviousWindowCommand())
