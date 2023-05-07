import logging
from datetime import datetime

from .settings import BASE_APP_PATH

 
# Stdout handler
class StdoutHandler(logging.Handler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.formatter = logging.Formatter("[%(levelname)s][%(name)s] %(message)s")

    def emit(self, record):
        print(self.formatter.format(record))


# FileHandler
LOG_DIRECTORY = BASE_APP_PATH / "logs"
LOG_DIRECTORY.mkdir(parents=True, exist_ok=True)
log_file_name = LOG_DIRECTORY / "cart_player.log"
file_handler = logging.FileHandler(filename=log_file_name)
file_handler.suffix = "%Y-%m-%d"
file_handler.setLevel(logging.INFO)
file_handler_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_handler_formatter)


logging_handlers = [StdoutHandler(), file_handler]


def logging_shutdown():
    logging.shutdown()
    new_log_file_name = LOG_DIRECTORY / f"cart_player-{datetime.now():%Y-%m-%d_%H-%M-%S}.log"
    log_file_name.rename(new_log_file_name)
