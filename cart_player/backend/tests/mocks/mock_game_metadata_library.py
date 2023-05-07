from typing import Dict

from cart_player.backend.domain.models import CartInfo, GameMetadata
from cart_player.backend.domain.ports import GameMetadataLibrary
from cart_player.core.exceptions import GameMetadataNotFoundException


class MockGameMetadataLibrary(GameMetadataLibrary):
    def __init__(self):
        self._db: Dict[str, GameMetadata] = {}

    def get_metadata(self, cart_info: CartInfo) -> GameMetadata:
        try:
            return self._db[cart_info.id]
        except KeyError:
            raise GameMetadataNotFoundException

    def add_info(self, id: str, info: dict):
        self._db[id] = GameMetadata(
            name=info.get("name", None),
            description=info.get("description", None),
            platform=info.get("platform", None),
            genre=info.get("genre", None),
            developer=info.get("developer", None),
            region=info.get("region", None),
            release=info.get("release", None),
        )
