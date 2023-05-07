import abc
import logging
from collections import defaultdict
from queue import Queue
from typing import Any, Dict, Optional
from uuid import UUID, uuid4

from cart_player.core import config

logger = logging.getLogger(f"{config.LOGGER_NAME}::Channel")


class ChannelSubscriber(abc.ABC):
    @abc.abstractmethod
    def is_supported(self, message: Any) -> bool:
        """Return True if the provided message is supported by this broker, False else."""
        pass


class Channel:
    """Communication channel for transmitting messages to supported subscribers."""

    def __init__(self):
        self._subscribers_by_id: Dict[UUID, ChannelSubscriber] = {}
        self._queues: Dict[str, Queue] = defaultdict(Queue)
        self._ignored = []

    def register(self, subscriber: ChannelSubscriber) -> UUID:
        """Register the provided subscriber and return its ID.

        Args:
            subscriber: Subscriber to register.
        """
        if subscriber in self._subscribers_by_id.values():
            logger.info("Subscriber has already been registered.", exc_info=True)
            return {v: k for k, v in self._subscribers_by_id.items()}[subscriber]

        id = uuid4()
        self._subscribers_by_id[id] = subscriber
        return id

    def ignore(self, message_type: Any):
        """Ignore a type of message (precedence over messages handled by registered subscribers).

        Args:
            message_type: Type of message to ignore.
        """
        self._ignored.append(message_type)

    def put(self, message: Any):
        """Transmit the provided message.

        Args:
            message: Message to transmit.
        """
        if type(message) in self._ignored:
            return

        not_emitted = True
        for id, subscriber in self._subscribers_by_id.items():
            if subscriber.is_supported(message):
                logger.debug(f"Put message on queue {id=}: {message}")
                self._queues[id].put(message)
                not_emitted = False

        if not_emitted:
            logger.info(f"No subscriber found for message: {message}", exc_info=True)

    def get(self, id: UUID, timeout: Optional[float] = None) -> Any:
        """Retrieve a message addressed to the subscriber whose ID has been provided.

        Args:
            timeout: Maximal time in seconds to wait for the message.

        Raises:
            Queue.Empty: If timeout has been reached without any message received.
        """
        return self._queues[id].get(timeout=timeout)
