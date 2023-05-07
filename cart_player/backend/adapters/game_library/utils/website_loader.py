import logging
from enum import Enum
from typing import Callable, Optional

import requests

from cart_player.backend import config

logger = logging.getLogger(f"{config.LOGGER_NAME}::Loader")


class ResponseType(str, Enum):
    TEXT = "text"
    CONTENT = "content"


class WebsiteLoader:
    """Helper class for loading the content of a website from a given URL."""

    def load(
        self,
        url: str,
        process_url: Callable[[str], str] = lambda _url: _url,
        spoof_user_agent: bool = True,
        reponse_type: ResponseType = ResponseType.TEXT,
    ) -> Optional[str]:
        """Load content from an url.

        Args:
            url: Url from which to load content.
            spoof_user_agent: True if user-agent must be overriden by a Safari browser user-agent.

        Returns:
            Content if content could be loaded, None otherwise.
        """
        # Process url
        url = process_url(url)
        if url is None:
            return None

        logger.debug(f"processed url: {url}")

        # Define a user-agent as Safari web browser
        headers = {}
        if spoof_user_agent:
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Windows; U; Windows CE) "
                    "AppleWebKit/535.19.4 (KHTML, like Gecko) "
                    "Version/4.0.2 Safari/535.19.4"
                )
            }

        # Perform the request
        try:
            response = requests.get(process_url(url), headers=headers)
        except Exception as e:
            logger.error(f"An error occurred during request [GET {url}]: {e}", exc_info=True)
            return None
        else:
            if response.status_code == 200:
                return response.text if reponse_type == ResponseType.TEXT else response.content
            return None
