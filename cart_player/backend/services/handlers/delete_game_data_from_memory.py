from typing import Optional, Type

from cart_player.backend.domain.commands import DeleteGameDataFromMemoryCommand
from cart_player.backend.domain.events import GameDataDeletedEvent
from cart_player.backend.domain.models import CartInfo, GameMetadata
from cart_player.backend.domain.ports import GameLibrary, Memory
from cart_player.backend.utils.models import GameDataType
from cart_player.core import Broker, Handler


class DeleteGameDataFromMemoryHandler(Handler):
    """Handle event 'DeleteGameDataFromMemoryCommand'."""

    def __init__(self, broker: Broker, memory: Memory, game_library: GameLibrary):
        super().__init__(broker)
        self.memory = memory
        self.game_library = game_library

    @property
    def message_type(self) -> Type:
        return DeleteGameDataFromMemoryCommand

    def _handle(self, cmd: DeleteGameDataFromMemoryCommand):
        cart_info = CartInfo.create(cmd.cart_info)
        game_metadata_data = self.memory.get_by_name(cart_info.metadata_filename, GameDataType.METADATA, True)
        game_metadata = (
            GameMetadata.create_from_bytes(game_metadata_data.content)
            if game_metadata_data
            else None
        )

        if game_metadata and cmd.type == GameDataType.METADATA:
            self.memory.delete_all(cart_info, type=GameDataType.METADATA, crc=game_metadata.crc)
            
            setattr(game_metadata, cmd.field, None)
            game_metadata.add_from(self.game_library.get_metadata(cart_info))
            self.memory.save(cart_info, content=game_metadata.bytes(), type=GameDataType.METADATA)

        else:
            crc = game_metadata.crc if game_metadata else None
            self.memory.delete_all(cart_info, type=cmd.type, crc=crc)
        
        self._publish(GameDataDeletedEvent(**cmd.dict()))
