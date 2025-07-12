import abc
import logging
from typing import List, Type

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
    def messages_types(self) -> List[Type]:
        """Types of messages handled by this handler."""
        return [self.message_type]

    @property
    def message_type(self) -> Type:
        """Type of message handled by this handler."""
        if len(self.messages_types) != 1:
            raise ValueError

        return next(iter(self.messages_types))

    def handle(self, message):
        """
        Handle the given message.

        Raises:
            RuntimeError: Type of message cannot be handled by this handler.
        """
        if all(not isinstance(message, message_type) for message_type in self.messages_types):
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
