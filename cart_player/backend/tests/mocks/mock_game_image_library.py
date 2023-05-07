import base64
from pathlib import Path
from typing import Dict

from cart_player.backend.domain.models import CartInfo, GameImage
from cart_player.backend.domain.ports import GameImageLibrary
from cart_player.core.exceptions import GameImageNotFoundException


class MockGameImageLibrary(GameImageLibrary):
    def __init__(self):
        self._db: Dict[str, GameImage] = {}

    def get_image(self, cart_info: CartInfo) -> GameImage:
        try:
            return self._db[cart_info.id]
        except KeyError:
            raise GameImageNotFoundException

    def add_image(self, id: str, image_filepath: Path):
        with open(image_filepath, "rb") as image_file:
            self._db[id] = GameImage(data=base64.b64encode(image_file.read()))
