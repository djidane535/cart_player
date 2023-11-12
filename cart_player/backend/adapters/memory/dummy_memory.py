import abc
from typing import List, Optional

from cart_player.backend.domain.dtos import MemoryConfiguration
from cart_player.backend.domain.models import CartInfo, GameData
from cart_player.backend.domain.ports import Memory
from cart_player.backend.utils.models import GameDataType


class DummyMemory(Memory):
    """Dummy memory doing nothing."""

    def save(self, cart_info: CartInfo, content: bytes, type: GameDataType, metadata: dict = {}):
        return

    def get_by_name(self, name: str, type: GameDataType, with_content: bool = False) -> Optional[GameData]:
        return None

    def get_all(
        self,
        cart_info: CartInfo,
        type: Optional[GameDataType] = None,
        with_content: bool = False,
    ) -> List[GameData]:
        return []

    def update_configuration(self, dto: MemoryConfiguration):
        return
