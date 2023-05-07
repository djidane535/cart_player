import abc
from typing import List, Optional

from cart_player.backend.domain.dtos import MemoryConfiguration
from cart_player.backend.domain.models import CartInfo, GameData
from cart_player.backend.utils.models import GameDataType


class Memory(abc.ABC):
    """Storage dedicated to cart games and saves."""

    @abc.abstractmethod
    def save(self, cart_info: CartInfo, content: bytes, type: GameDataType, metadata: dict = {}):
        """Save content into memory.

        Args:
            cart_info: Information about the cart whose content has to be saved.
            type: Type of game data.
            metadata: Metadata of the file to save. May be required for some GameDataTypes.
                      (see concrete implementation)

        Raises:
            RuntimeError: If unable to save content into memory.
            ValueError: If mandatory data is missing in metadata (see concrete implementation).
        """
        pass

    @abc.abstractmethod
    def get_by_name(self, name: str, type: GameDataType, with_content: bool = False) -> Optional[GameData]:
        """Return the requested game data associated with the provided name (<filename>.<extension>).

        Args:
            name: Name of the game data to be retrieved
            type: Type of game data to retrieve. If SAVE, returns the most recent one.
            with_content: True if content must be retrieved, False else.

        Returns:
            Game data associated to the provided name, None if no game data has been found.
        """
        pass

    @abc.abstractmethod
    def get_all(
        self,
        cart_info: CartInfo,
        type: Optional[GameDataType] = None,
        with_content: bool = False,
    ) -> List[GameData]:
        """Return the list of all game data associated to the provided cart_info.

        Args:
            cart_info: Information about the cart whose game data has to be retrieved.
            type: Type of game data to retrieve. If None, all types of game data are returned.
            with_content: True if content must be retrieved, False else.

        Returns:
            The list of all game data associated to the provided cart_info.
        """
        pass

    @abc.abstractmethod
    def update_configuration(self, dto: MemoryConfiguration):
        """Update memory configuration.

        Args:
            dto: Memory configuration.
        """
        pass
