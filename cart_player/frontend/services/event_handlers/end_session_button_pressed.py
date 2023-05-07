from typing import Type

from cart_player.core import Broker, Handler
from cart_player.frontend.domain.events import EndSessionButtonPressedEvent, PopUpWindowIsClosingEvent
from cart_player.frontend.domain.ports import App


class EndSessionButtonPressedEventHandler(Handler):
    """Handle event 'EndSessionButtonPressedEvent'."""

    def __init__(self, broker: Broker, app: App):
        super().__init__(broker)
        self._app = app

    @property
    def message_type(self) -> Type:
        return EndSessionButtonPressedEvent

    def _handle(self, evt: EndSessionButtonPressedEvent):
        self._app.end_game_session()
        self._publish(
            PopUpWindowIsClosingEvent(
                play_window_is_closing=evt.play_window_is_closing,
                cart_info=evt.cart_info,
                game_session_path=evt.game_session_path,
            )
        )
