from datetime import datetime
from typing import Optional

from cart_player.backend.utils.models import GameDataType


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
