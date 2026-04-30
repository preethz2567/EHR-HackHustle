import logging

def setup_logger():
    logging.basicConfig(level=logging.INFO)

def log_info(message):
    logging.info(message)

def log_error(message):
    logging.error(message)

def log_warning(message):
    logging.warning(message)
