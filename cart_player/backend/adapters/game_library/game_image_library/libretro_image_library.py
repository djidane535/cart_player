import base64
import logging
import time
from io import BytesIO
from urllib.parse import quote

from PIL import Image

from cart_player.backend import config
from cart_player.backend.adapters.game_library.utils import LibretroImageParser, ResponseType, WebsiteLoader
from cart_player.backend.adapters.game_library.utils.libretro_settings import (
    IMAGE_EXTENSION,
    LIBRETRO_GAMEBOY_ADVANCE_SUBPATH,
    LIBRETRO_GAMEBOY_COLOR_SUBPATH,
    LIBRETRO_GAMEBOY_SUBPATH,
    LIBRETRO_GITHUB_IMAGE_TYPE_SUBPATH,
    LIBRETRO_GITHUB_THUMBNAILS_DOMAIN,
)
from cart_player.backend.domain.models import CartInfo, GameImage
from cart_player.backend.domain.ports import GameImageLibrary
from cart_player.backend.utils.models import GameSupport

logger = logging.getLogger(f"{config.LOGGER_NAME}::LibretroImageLibrary")


class LibretroImageLibrary(GameImageLibrary):
    def __init__(self):
        self.loader = WebsiteLoader()
        self.parser = LibretroImageParser()

    def get_image(self, cart_info: CartInfo) -> GameImage:
        support_subpath = self._get_support_subpath(cart_info.support)
        cart_id = cart_info.id
        while "(" in cart_id:
            url = (
                f"{LIBRETRO_GITHUB_THUMBNAILS_DOMAIN}/{support_subpath}/"
                f"{LIBRETRO_GITHUB_IMAGE_TYPE_SUBPATH}/{quote(cart_info.id, safe='()')}{IMAGE_EXTENSION}"
            )
            logger.debug(f"Fetching game image from: {url}")
            content = self._validate_content(self.loader.load(url, reponse_type=ResponseType.CONTENT))
            if content is None:
                cart_id = "(".join(cart_id.split("(")[:-1])
                time.sleep(0.25)
                continue

            return self.parser.parse_content(content, cart_info)

        return GameImage()

    def _validate_content(self, content: bytes):
        try:
            Image.open(BytesIO(content))
            return content
        except Exception:
            try:
                Image.open(BytesIO(base64.b64decode(content)))
                return base64.b64decode(content)
            except Exception:
                return None

    def _get_support_subpath(cls, support: GameSupport) -> str:
        return {
            GameSupport.GAMEBOY: LIBRETRO_GAMEBOY_SUBPATH,
            GameSupport.GAMEBOY_OR_GAMEBOY_COLOR: LIBRETRO_GAMEBOY_COLOR_SUBPATH,
            GameSupport.GAMEBOY_COLOR: LIBRETRO_GAMEBOY_COLOR_SUBPATH,
            GameSupport.GAMEBOY_ADVANCE: LIBRETRO_GAMEBOY_ADVANCE_SUBPATH,
        }[support]
