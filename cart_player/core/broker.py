from __future__ import annotations

import logging
import queue
import traceback
from collections import defaultdict
from typing import Any, Dict, List, Optional

from cart_player.core import config
from cart_player.core.domain.events import UnexpectedErrorEvent

from .channel import Channel, ChannelSubscriber
from .handler import Handler

logger = logging.getLogger(f"{config.LOGGER_NAME}::Broker")


class Broker(ChannelSubscriber):
    """Broker for dispatching messages to registered handlers.

    Args:
        channel: Communication channel, through which all messages are transported.
    """

    def __init__(self, channel: Channel):
        self._id = channel.register(self)
        self._channel = channel
        self._message_handler_mapping: Dict[Any, List[Handler]] = defaultdict(list)

    def is_supported(self, message: Any) -> bool:
        return type(message) in self._message_handler_mapping

    def register(self, handler: Handler):
        """Register a handler.

        Args:
            handler: Handler to register.
        """
        self._message_handler_mapping[handler.message_type].append(handler)

    def publish_and_execute(
        self,
        message: Any,
        limit: Optional[int] = None,
        timeout: Optional[float] = None,
    ):
        """Publish a message and process all messages until the limit or timeout has been reached.

        Args:
            limit: Maximum number of messages to handle.
            timeout: Maximal time in seconds to wait for the next message to handle.
                     If None, wait until a message arrives.
        """
        self.publish(message)
        self.execute(limit, timeout)

    def publish(self, message: Any):
        """Publish a message.

        Args:
            message: Message to publish.
        """
        if message is None:
            logger.info(f"[{str(self._id)}] None message received: message has been discarded.", exc_info=True)
            return
        self._channel.put(message)
        logger.info(f"[{str(self._id)}] publish(): {message=}")

    def execute(self, limit: Optional[int] = None, timeout: Optional[float] = None):
        """Process all messages until the limit or timeout has been reached.

        Args:
            limit: Maximum number of messages to handle.
            timeout: Maximal time in seconds to wait for the next message to handle.
                     If None, wait until a message arrives.
        """
        while limit is None or limit > 0:
            limit = limit - 1 if limit is not None else None
            try:
                message = self._channel.get(self._id, timeout=timeout)
            except queue.Empty:  # timeout has been reached
                return

            logger.info(f"[{str(self._id)}] execute(): {message=}")

            handlers = self._message_handler_mapping[type(message)]
            if not handlers:
                logger.info(f"[{str(self._id)}] No handler found for message: {message}", exc_info=True)
                continue

            try:
                for handler in handlers:
                    handler.handle(message)
            except Exception:
                self.publish(
                    UnexpectedErrorEvent(
                        message=f"Error during handler execution (handler={handler.__class__.__name__}, {message=}).",
                        trace=traceback.format_exc(),
                        close_app=True,
                    )
                )
