import abc
import logging
import traceback
from typing import Optional

from cart_player.backend import config
from cart_player.backend.domain.models import CartInfo, GameMetadata

logger = logging.getLogger(f"{config.LOGGER_NAME}::GameMetadataParser")


class GameMetadataParser(abc.ABC):
    """Abstract base class for parsing game metadata from a text source.

    Subclasses must implement the `_parse_text` method, which actually performs the parsing operation.
    """

    def parse_text(self, text: Optional[str], cart_info: CartInfo) -> GameMetadata:
        """Parse the text and extract game metadata.

        Args:
            text: Text to be parsed.
            cart_info: Cart info.

        Returns:
            Game metadata extracted from the text.
        """
        if not text:
            return GameMetadata()

        try:
            return self._parse_text(text, cart_info)
        except Exception as e:
            logger.error(f"An error occurred while parsing metadata: {e}", exc_info=True)
            return GameMetadata()

    @abc.abstractmethod
    def _parse_text(self, text: str, cart_info: CartInfo) -> GameMetadata:
        """Parse the text and extract game metadata.
        Actually perform the parsing operation.

        Args:
            text: Text to be parsed.
            carinfo: Cart info.

        Returns:
            Game metadata extracted from the text.
        """
        raise NotImplementedError
