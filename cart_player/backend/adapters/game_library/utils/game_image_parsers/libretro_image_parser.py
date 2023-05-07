import base64

from cart_player.backend.domain.models import CartInfo, GameImage

from .game_image_parser import GameImageParser


class LibretroImageParser(GameImageParser):
    def _parse_content(self, content: str, cart_info: CartInfo) -> GameImage:
        data = base64.b64encode(content)
        return GameImage(data=data)
