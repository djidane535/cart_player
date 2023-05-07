import logging

from .logging_handlers import logging_handlers

LOGGER_NAME = __package__


# Logger handlers
[logging.root.addHandler(handler) for handler in logging_handlers]
