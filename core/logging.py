import logging


logging.root.setLevel(logging.INFO)
logging.basicConfig(level=logging.INFO)


def get_logger():
    return logging.getLogger()
