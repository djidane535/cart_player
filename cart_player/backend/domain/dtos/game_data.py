from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from cart_player.backend.utils.models import GameDataType


class GameData(BaseModel):
    name: str
    date: datetime
    type: GameDataType
    metadata: Optional[dict]
