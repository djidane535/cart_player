from typing import Type

from cart_player.backend.api.commands import UpdateGameDataFromMemoryCommand
from cart_player.backend.utils.models import GameDataType
from cart_player.core import Handler
from cart_player.frontend.domain.commands import RestorePreviousWindowCommand
from cart_player.frontend.domain.events import EditApplyButtonPressed
from cart_player.frontend.utils.models import EditWindowType


class EditApplyButtonPressedEventHandler(Handler):
    """Handle event 'EditApplyButtonPressed'."""

    @property
    def message_type(self) -> Type:
        return EditApplyButtonPressed

    def _handle(self, evt: EditApplyButtonPressed):
        if not evt.has_value or not evt.cart_info or evt.cart_info.is_empty:
            self._publish(RestorePreviousWindowCommand())
            return
        
        game_data_type = self._get_game_data_type(evt.edit_type)
        if game_data_type == GameDataType.IMAGE:
            self._publish(
                UpdateGameDataFromMemoryCommand(
                    cart_info=evt.cart_info, 
                    type=game_data_type, 
                    path=evt.image_path,
                )
            )
            return
        
        if game_data_type == GameDataType.METADATA:
            metadata_field = self._get_metadata_field(evt.edit_type)
            self._publish(
                UpdateGameDataFromMemoryCommand(
                    cart_info=evt.cart_info, 
                    type=game_data_type, 
                    field=metadata_field, 
                    text=evt.text,
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
