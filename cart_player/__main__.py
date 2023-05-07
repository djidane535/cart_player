import logging
import os
import time
from pathlib import Path
from threading import Thread

from cart_player import config
from cart_player.frontend.domain.ports import AppStatus
from cart_player.logging_handlers import logging_shutdown

logger = logging.getLogger("__main__")


def consume_messages(id, stop):
    while True:
        # set timeout to check regularly if thread should be stopped
        config.broker.execute(timeout=0.5)
        if stop():
            logger.debug(f"Broker worker stopped: {id=}")
            break


def interrupt_app_event_reading(stop):
    while True:
        # Wake-up app from its blocking event reading process
        if config.app._windows:
            config.app._windows[-1].write_event_value("-NO_WINDOW_EVENT-", None)  # TODO use abstract interface

        # check regularly if thread should be stopped
        time.sleep(0.5)
        if stop():
            logger.debug("Broker worker stopped: <app periodic wake-up>")
            break


if __name__ == "__main__":
    # Ensure app is running from the right directory (dev and prod)
    os.chdir(str(Path(__file__).parent))
    current_dir_path = Path(os.getcwd())
    if str(current_dir_path).endswith("cart_player"):
        os.chdir(str(current_dir_path.parent))

    # Workers for broker executed by child threads
    n_workers = 4
    stop_threads = False
    broker_workers = [Thread(target=consume_messages, args=(i, lambda: stop_threads)) for i in range(n_workers)]
    broker_workers.append(Thread(target=interrupt_app_event_reading, args=(lambda: stop_threads,)))
    [broker_worker.start() for broker_worker in broker_workers]

    # Frontend
    config.app.start()
    while config.app.status != AppStatus.NOT_RUNNING:
        event = config.app.wait_for_event()
        config.main_broker.publish_and_execute(event, timeout=0)

    # Stop all workers
    stop_threads = True
    [broker_worker.join() for broker_worker in broker_workers]

    logger.debug("Exit main thread")
    logging_shutdown()
