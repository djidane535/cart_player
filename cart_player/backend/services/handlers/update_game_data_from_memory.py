import base64
import logging
from io import BytesIO
from typing import Optional, Type

from PIL import Image

from cart_player.backend import config
from cart_player.backend.domain.commands import UpdateGameDataFromMemoryCommand
from cart_player.backend.domain.events import GameDataUpdatedEvent
from cart_player.backend.domain.models import CartInfo, GameMetadata
from cart_player.backend.domain.ports import Memory
from cart_player.backend.utils.models import GameDataType, MemoryOnExistMode
from cart_player.core import Broker, Handler

logger = logging.getLogger(f"{config.LOGGER_NAME}::UpdateGameDataFromMemoryHandler")

class UpdateGameDataFromMemoryHandler(Handler):
    """Handle event 'UpdateGameDataFromMemoryCommand'."""

    def __init__(self, broker: Broker, memory: Memory):
        super().__init__(broker)
        self.memory = memory

    @property
    def message_type(self) -> Type:
        return UpdateGameDataFromMemoryCommand

    def _handle(self, cmd: UpdateGameDataFromMemoryCommand):
        cart_info = CartInfo.create(cmd.cart_info)
        
        if cmd.type == GameDataType.IMAGE:
            self._update_image(cart_info, cmd.path)
            
        if cmd.type == GameDataType.METADATA:
            cart_info = self._update_metadata(cart_info, cmd.field, cmd.text)

        cmd.cart_info = cart_info.to_dto()
        self._publish(GameDataUpdatedEvent(**cmd.dict()))

    def _update_image(self, cart_info: CartInfo, image_filepath: str):
        image = Image.open(image_filepath)
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        content = base64.b64encode(buffer.getvalue())
        buffer.close()

        self.memory.save(cart_info, content, GameDataType.IMAGE, on_exist=MemoryOnExistMode.NOTHING)
    
    def _update_metadata(self, cart_info: CartInfo, field: str, value: str) -> CartInfo:
        game_metadata_data = self.memory.get_by_name(cart_info.metadata_filename, GameDataType.METADATA, True)
        if not game_metadata_data:
            return cart_info
        
        if field == "name":
            return self._update_name(cart_info, value)

        game_metadata = GameMetadata.create_from_bytes(game_metadata_data.content)
        if field == "crc" and game_metadata.crc:
            self.memory.delete_all(cart_info, GameDataType.ANALOGUE_POCKET_IMAGE, game_metadata.crc)

        setattr(game_metadata, field, value)
        self.memory.save(cart_info, game_metadata.bytes(), GameDataType.METADATA, on_exist=MemoryOnExistMode.NOTHING)

        return cart_info

    def _update_name(self, cart_info: CartInfo, name: str) -> CartInfo:
        updated_cart_info = CartInfo.create(cart_info.to_dto())
        updated_cart_info.id_override = name
        
        # Name already used
        types = [t for t in list(GameDataType) if t not in (GameDataType.CART, GameDataType.ANALOGUE_POCKET_IMAGE)]
        if any(self.memory.get_all(updated_cart_info, type=type) for type in types):
            logger.warning(f"Name '{name}' is already used: operation cancelled.")
            return cart_info

        # Get all data
        game_data_list = self.memory.get_all(cart_info, with_content=True)
        for game_data in game_data_list:
            game_data.update(name=name)

        # Update retrieved data and save it
        for game_data in game_data_list:
            if game_data.type == GameDataType.IMAGE:
                self.memory.save(updated_cart_info, base64.b64encode(game_data.content), game_data.type, game_data.metadata)
            else:
                self.memory.save(updated_cart_info, game_data.content, game_data.type, game_data.metadata)
        
        # Delete old data
        crc = self._get_crc(cart_info)
        types = [
            type
            for type in list(GameDataType)
            if type not in [GameDataType.CART, GameDataType.ANALOGUE_POCKET_IMAGE]
        ]
        for type in types:
            self.memory.delete_all(cart_info, type=type, crc=crc)

        return updated_cart_info

    def _get_crc(self, cart_info: CartInfo) -> Optional[str]:
        game_metadata_data = self.memory.get_by_name(cart_info.metadata_filename, GameDataType.METADATA, True)
        if not game_metadata_data:
            return None
        
        game_metadata = GameMetadata.create_from_bytes(game_metadata_data.content)
        return game_metadata.crc