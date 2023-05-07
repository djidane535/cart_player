import abc
import logging
from typing import Type

from cart_player.core import config

logger = logging.getLogger(f"{config.LOGGER_NAME}::Handler")


class Handler(abc.ABC):
    """Interface for handlers.

    Args:
        broker: Broker.
    """

    def __init__(self, broker):
        self._broker = broker

    @property
    @abc.abstractmethod
    def message_type(self) -> Type:
        """Type of message handled by this handler."""
        pass

    def handle(self, message):
        """
        Handle the given message.

        Raises:
            RuntimeError: Type of message cannot be handled by this handler.
        """
        if not isinstance(message, self.message_type):
            raise RuntimeError(
                f"Message of type '{type(message)}' cannot be handled by this handler (expected: {self.message_type})",
            )

        logger.debug(f"handle(): {message=}")
        self._handle(message)

    @abc.abstractmethod
    def _handle(self, message):
        """Perform the actual message handling. Message is guaranteed to be of the correct type."""
        pass

    def _publish(self, message):
        """Publish a message."""
        self._broker.publish(message)
