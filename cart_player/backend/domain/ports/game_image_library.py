import abc

from cart_player.backend.domain.models import CartInfo, GameImage


class GameImageLibrary(abc.ABC):
    """Game image library, providing images based on cart info."""

    @abc.abstractmethod
    def get_image(self, cart_info: CartInfo) -> GameImage:
        """Return the game image corresponding to the provided cart info.

        Args:
            cart_info: Cart info.
            image_type: Type of image to retrieve.

        Returns:
            Game image corresponding to the provided cart info.
            If it cannot be found, an empty game image is returned instead.
        """
        pass
