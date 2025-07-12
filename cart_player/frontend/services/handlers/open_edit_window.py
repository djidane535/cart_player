from typing import List, Type

from cart_player.core import Broker, Handler
from cart_player.frontend.domain.events import (
    EditGameCartBoxImageEvent,
    EditGameCRCEvent,
    EditGameDescriptionEvent,
    EditGameDeveloperEvent,
    EditGameGenreEvent,
    EditGameNameEvent,
    EditGamePlatformEvent,
    EditGameRegionEvent,
    EditGameReleaseEvent,
)
from cart_player.frontend.domain.ports import App


class OpenEditWindowHandler(Handler):
    """Handle event 'OpenEditWindowHandler'."""

    def __init__(self, broker: Broker, app: App):
        super().__init__(broker)
        self._app = app

    @property
    def messages_types(self) -> List[Type]:
        return [
            EditGameCartBoxImageEvent,
            EditGameNameEvent,
            EditGameDescriptionEvent,
            EditGamePlatformEvent,
            EditGameGenreEvent,
            EditGameDeveloperEvent,
            EditGameRegionEvent,
            EditGameReleaseEvent,
            EditGameCRCEvent,
        ]

    def _handle(self, evt: EditGameCartBoxImageEvent):
        self._app.open_edit_window(evt.type)
