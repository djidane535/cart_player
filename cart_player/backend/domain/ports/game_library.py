from typing import List

from cart_player.backend.domain.models import CartInfo, GameImage, GameMetadata
from cart_player.core.exceptions import GameImageNotFoundException, GameMetadataNotFoundException

from .game_image_library import GameImageLibrary
from .game_metadata_library import GameMetadataLibrary


class GameLibrary:
    """Game library, providing information and images based on cart info."""

    def __init__(
        self,
        metadata_libraries: List[GameMetadataLibrary],
        image_libraries: List[GameImageLibrary],
    ):
        self._metadata_libraries = metadata_libraries
        self._image_libraries = image_libraries

    def get_image(self, cart_info: CartInfo) -> GameImage:
        """Return the game image corresponding to the provided cart info.

        Args:
            cart_info: Cart info.
            image_type: Type of image to retrieve.

        Returns:
            Game image corresponding to the provided cart info.
            If it cannot be found, an empty game image is returned instead.
        """
        for image_library in self._image_libraries:
            try:
                return image_library.get_image(cart_info)
            except GameImageNotFoundException:
                continue

        return GameImage()

    def get_metadata(self, cart_info: CartInfo) -> GameMetadata:
        """Return the game metadata corresponding to the provided cart info.

        Args:
            cart_info: Cart info.

        Returns:
            Game metadata corresponding to the provided cart info.
            If it cannot be found, an empty game metadata is returned instead.
        """
        game_metadata = GameMetadata()
        for metadata_library in self._metadata_libraries:
            try:
                new_game_metadata = metadata_library.get_metadata(cart_info)
            except GameMetadataNotFoundException:
                continue

            game_metadata.add_from(new_game_metadata)
            if game_metadata.is_complete():
                break

        return game_metadata
