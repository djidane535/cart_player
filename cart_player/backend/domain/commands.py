from pathlib import Path
from typing import Optional

from pydantic import root_validator

from cart_player.backend.domain.dtos import (
    CartInfo,
    GameImage,
    GameMetadata,
    GBXFlasherConfiguration,
    LocalMemoryConfiguration,
)
from cart_player.backend.utils.models import GameDataType
from cart_player.core.domain.messages import BaseMessage


class BackupCartSaveCommand(BaseMessage):
    cart_info: CartInfo


class BackupSaveFileAfterPlayingCommand(BaseMessage):
    cart_info: CartInfo
    target_path: Path


class DeleteGameDataFromMemoryCommand(BaseMessage):
    cart_info: CartInfo
    type: GameDataType
    # METADATA
    field: Optional[str] = None


class EraseCartSaveCommand(BaseMessage):
    cart_info: CartInfo


class ExportToAnaloguePocketLibraryCommand(BaseMessage):
    cart_info: CartInfo
    game_image: GameImage
    game_metadata: GameMetadata


class InstallCartGameCommand(BaseMessage):
    cart_info: CartInfo


class ReadCartDataCommand(BaseMessage):
    cart_info: Optional[CartInfo]
    skip_game_data: bool = False
    skip_game_metadata: bool = False
    skip_game_image: bool = False
    raise_error: bool = True


class SetupGameFileAndSaveFileForPlayingCommand(BaseMessage):
    game_name: str
    save_name: Optional[str] = None
    target_path: Path


class UpdateGameDataFromMemoryCommand(BaseMessage):
    cart_info: CartInfo
    type: GameDataType
    # IMAGE
    path: Optional[Path] = None
    # METADATA
    field: Optional[str] = None
    text: Optional[str] = None

    @root_validator
    def validate_is_single_type(cls, values):
        if not (cls._validate_is_image(values) ^ cls._validate_is_metadata(values)):
            raise ValueError
        
        return values
    
    @staticmethod
    def _validate_is_image(values) -> bool:
        return bool(values.get("path", None))
    
    @staticmethod
    def _validate_is_metadata(values) -> bool:
        return bool(values.get("field", None)) and bool(values.get("text", None))


class UpdateLocalMemoryConfigurationCommand(LocalMemoryConfiguration, BaseMessage):
    pass


class UpdateGBXFlasherConfigurationCommand(GBXFlasherConfiguration, BaseMessage):
    pass


class WriteCartSaveCommand(BaseMessage):
    cart_info: CartInfo
    save_name: str
