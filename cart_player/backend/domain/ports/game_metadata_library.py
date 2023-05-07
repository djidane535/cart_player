import abc

from cart_player.backend.domain.models import CartInfo, GameMetadata


class GameMetadataLibrary(abc.ABC):
    """Game metadata library, providing information based on cart info."""

    @abc.abstractmethod
    def get_metadata(self, cart_info: CartInfo) -> GameMetadata:
        """Return the game metadata corresponding to the provided cart info.

        Args:
            cart_info: Cart info.

        Returns:
            Game metadata corresponding to the provided cart info.
            If it cannot be found, an empty game metadata is returned instead.
        """
        pass
