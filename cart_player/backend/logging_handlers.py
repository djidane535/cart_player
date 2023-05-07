import logging
import traceback


# Publish an event for WARNING and ERROR messages
class EventPublisherHandler(logging.Handler):
    def emit(self, record):
        # WARNING messages
        if record.levelno == logging.WARNING:
            from cart_player.config import main_broker
            from cart_player.core.domain.events import UnexpectedWarningEvent

            main_broker.publish(UnexpectedWarningEvent(message=record.getMessage(), trace=traceback.format_exc()))

        # ERROR messages
        if record.levelno == logging.ERROR:
            from cart_player.config import main_broker
            from cart_player.core.domain.events import UnexpectedErrorEvent

            main_broker.publish(
                UnexpectedErrorEvent(message=record.getMessage(), trace=traceback.format_exc(), close_app=False)
            )


logging_handlers = [EventPublisherHandler()]
