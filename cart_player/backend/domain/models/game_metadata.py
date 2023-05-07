from __future__ import annotations

import pickle
from typing import Optional

from cart_player.backend.domain.dtos import GameMetadata as GameMetadataDTO


class GameMetadata:
    """Game metadata.

    Args:
        name: Game name.
        description: Game description.
        platform: Game platform.
        genre: Game genre.
        developer: Game developer.
        region: Game region.
        release: Game release.
        crc: CRC.

    Attributes:
        name: Game name.
        description: Game description.
        platform: Game platform.
        genre: Game genre.
        developer: Game developer.
        region: Game region.
        release: Game release.
        crc: CRC.
    """

    def __init__(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        platform: Optional[str] = None,
        genre: Optional[str] = None,
        developer: Optional[str] = None,
        region: Optional[str] = None,
        release: Optional[str] = None,
        crc: Optional[str] = None,
    ):
        self.name = name
        self.description = description
        self.platform = platform
        self.genre = genre
        self.developer = developer
        self.region = region
        self.release = release
        self.crc = crc

    def add_from(self, game_metadata: GameMetadata):
        """Add missing info from the provided game metadata.

        Args:
            game_metadata: Game metadata to be used to fill up gaps in this game metadata.
        """

        self.name = self.name or game_metadata.name
        self.description = self.description or game_metadata.description
        self.platform = self.platform or game_metadata.platform
        self.genre = self.genre or game_metadata.genre
        self.developer = self.developer or game_metadata.developer
        self.region = self.region or game_metadata.region
        self.release = self.release or game_metadata.release
        self.crc = self.crc or game_metadata.crc

    def is_empty(self) -> bool:
        """Return True if this game metadata contains no info for any field, False otherwise.

        Returns:
            True if this game metadata contains no info for any fields, False otherwise.
        """
        return all(
            [
                not self.name,
                not self.description,
                not self.platform,
                not self.genre,
                not self.developer,
                not self.region,
                not self.release,
                not self.crc,
            ]
        )

    def is_complete(self) -> bool:
        """Return True if this game metadata contains info for all its fields, False otherwise.

        Returns:
            True if this game metadata contains info for all its fields, False otherwise.
        """

        return all(
            [
                self.name,
                self.description,
                self.platform,
                self.genre,
                self.developer,
                self.region,
                self.release,
                self.crc,
            ],
        )

    def bytes(self) -> bytes:
        return pickle.dumps(self.__dict__)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return False

    @staticmethod
    def create(dto: GameMetadataDTO):
        """Create a GameMetadata model from the provided DTO."""
        return GameMetadata(
            name=dto.name,
            description=dto.description,
            platform=dto.platform,
            genre=dto.genre,
            developer=dto.developer,
            region=dto.region,
            release=dto.release,
            crc=dto.crc,
        )

    @staticmethod
    def create_from_bytes(data: bytes):
        """Create a GameMetadata model from the provided data."""
        metadata_dict = pickle.loads(data)
        dto = GameMetadataDTO(**metadata_dict)
        return GameMetadata.create(dto)
