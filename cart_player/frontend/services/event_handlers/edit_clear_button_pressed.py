from typing import Type

from cart_player.backend.api.commands import DeleteGameDataFromMemoryCommand
from cart_player.backend.utils.models import GameDataType
from cart_player.core import Handler

# from cart_player.frontend.domain.commands import RestorePreviousWindowCommand
from cart_player.frontend.domain.events import EditClearButtonPressed
from cart_player.frontend.utils.models import EditWindowType


class EditClearButtonPressedEventHandler(Handler):
    """Handle event 'EditClearButtonPressed'."""

    @property
    def message_type(self) -> Type:
        return EditClearButtonPressed

    def _handle(self, evt: EditClearButtonPressed):
        if not evt.cart_info or evt.cart_info.is_empty:
            return
        
        if evt.edit_type == EditWindowType.GAME_NAME:
            return

        game_data_type = self._get_game_data_type(evt.edit_type)
        if game_data_type == GameDataType.IMAGE:
            self._publish(
                DeleteGameDataFromMemoryCommand(
                        cart_info=evt.cart_info,
                        type=game_data_type,
                    )
                )
            return
        if game_data_type == GameDataType.METADATA:
            metadata_field = self._get_metadata_field(evt.edit_type)
            self._publish(
                DeleteGameDataFromMemoryCommand(
                        cart_info=evt.cart_info,
                        type=game_data_type, 
                        field=metadata_field,
                    )
                )
            return
        
        raise ValueError(f"Unsupported edit type ({evt.edit_type=}).")

    @staticmethod
    def _get_game_data_type(type: EditWindowType) -> GameDataType:
        return {
            EditWindowType.GAME_BOX_IMAGE: GameDataType.IMAGE,
            EditWindowType.GAME_NAME: GameDataType.METADATA,
            EditWindowType.GAME_DESCRIPTION: GameDataType.METADATA,
            EditWindowType.GAME_PLATFORM: GameDataType.METADATA,
            EditWindowType.GAME_GENRE: GameDataType.METADATA,
            EditWindowType.GAME_DEVELOPER: GameDataType.METADATA,
            EditWindowType.GAME_REGION: GameDataType.METADATA,
            EditWindowType.GAME_RELEASE: GameDataType.METADATA,
            EditWindowType.GAME_CRC: GameDataType.METADATA,
        }[type]
    
    @staticmethod
    def _get_metadata_field(type: EditWindowType) -> str:
        return {
            EditWindowType.GAME_NAME: "name",
            EditWindowType.GAME_DESCRIPTION: "description",
            EditWindowType.GAME_PLATFORM: "platform",
            EditWindowType.GAME_GENRE: "genre",
            EditWindowType.GAME_DEVELOPER: "developer",
            EditWindowType.GAME_REGION: "region",
            EditWindowType.GAME_RELEASE: "release",
            EditWindowType.GAME_CRC: "crc",
        }[type]