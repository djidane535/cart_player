from pathlib import Path
from typing import Optional

from cart_player.backend.domain.dtos import CartInfo, GameImage, GameMetadata, LocalMemoryConfiguration
from cart_player.core.domain.messages import BaseMessage


class BackupCartSaveCommand(BaseMessage):
    pass


class BackupSaveFileAfterPlayingCommand(BaseMessage):
    cart_info: CartInfo
    target_path: Path


class EraseCartSaveCommand(BaseMessage):
    pass


class ExportToAnaloguePocketLibraryCommand(BaseMessage):
    cart_info: CartInfo
    game_image: GameImage
    game_metadata: GameMetadata


class InstallCartGameCommand(BaseMessage):
    pass


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


class UpdateLocalMemoryConfigurationCommand(LocalMemoryConfiguration, BaseMessage):
    pass


class WriteCartSaveCommand(BaseMessage):
    save_name: str
