import json
import pickle
from datetime import datetime
from typing import Optional

from cart_player.backend.utils.models import GameDataType

from .game_metadata import GameMetadata


class GameData:
    """Gathers game data.

    Args:
        name: Name of the game content.
        date: Date at which the data has been modified for the last time.
        content: Game content.
        type: Type of game content.
        extension: Extension of the file game content.
        metadata: Metadata.

    Attributes:
        name: Name of the game content.
        date: Date at which the data has been modified for the last time.
        content: Game content.
        type: Type of game content.
        extension: Extension of the file game content.
        metadata: Metadata.
    """

    def __init__(
        self,
        name: str,
        date: datetime,
        content: Optional[bytes],
        type: GameDataType,
        extension: Optional[str] = None,
        metadata: dict = None,
    ):
        self.name = name
        self.date = date
        self.content = content
        self.type = type
        self.extension = extension
        self.metadata = metadata

    def update(self, name: str):
        if self.type == GameDataType.METADATA:
            game_metadata: GameMetadata = GameMetadata.create_from_bytes(self.content)
            game_metadata.name = name
            self.content =game_metadata.bytes()

        if self.type == GameDataType.CART:
            cart: dict = pickle.loads(self.content)
            cart.update({"id_override": name})
            self.content = pickle.dumps(cart)
