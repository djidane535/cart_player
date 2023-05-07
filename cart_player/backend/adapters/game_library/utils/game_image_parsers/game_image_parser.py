import abc
import logging
import traceback
from typing import Optional

from cart_player.backend import config
from cart_player.backend.domain.models import CartInfo, GameImage

logger = logging.getLogger(f"{config.LOGGER_NAME}::GameImageParser")


class GameImageParser(abc.ABC):
    def parse_content(self, content: Optional[str], cart_info: CartInfo) -> GameImage:
        """Parse the content and extract game image.

        Args:
            content: Content to be parsed.
            cart_info: Cart info.

        Returns:
            Game image extracted from the content.
        """
        if not content:
            return GameImage()

        try:
            return self._parse_content(content, cart_info)
        except Exception as e:
            logger.error(f"An error occurred while parsing an image: {e}", exc_info=True)
            return GameImage()

    @abc.abstractmethod
    def _parse_content(self, content: str, cart_info: CartInfo) -> GameImage:
        """Parse the content and extract game image.
        Actually perform the parsing operation.

        Args:
            content: Content to be parsed.
            cart_info: Cart info.

        Returns:
            Game image extracted from the content.
        """
        raise NotImplementedError
