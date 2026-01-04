"""Test threading module in Python."""

import logging
import threading
import time


def thread_function(name):
    """Function to test threading."""
    logging.info("Thread %s: starting", name)
    logging.info("Thread %s: get_ident = %s", name, threading.get_ident())
    time.sleep(2)
    logging.info("Thread %s: finishing", name)


if __name__ == "__main__":
    LOG_FORMAT = "%(asctime)s: %(message)s"
    logging.basicConfig(format=LOG_FORMAT, level=logging.INFO, datefmt="%H:%M:%S")

    logging.info("Main    : before creating thread")
    logging.info("Main    : get_ident = %s", threading.get_ident())
    x = threading.Thread(target=thread_function, args=(1,), daemon=True)
    logging.info("Main    : before running thread")
    x.start()
    logging.info("Main    : wait for the thread to finish")
    logging.info("Main    : active_count = %s", threading.active_count())
    x.join()
    logging.info("Main    : all done")
