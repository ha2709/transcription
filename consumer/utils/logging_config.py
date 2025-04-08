# logging_config.py

import logging
import os
from logging.handlers import RotatingFileHandler

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FILE = os.getenv("LOG_FILE", "logs/app.log")
LOG_DIR = os.path.dirname(LOG_FILE)

if LOG_DIR and not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)


def setup_logging():
    # Clear existing handlers
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    logging.basicConfig(
        level=LOG_LEVEL,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),  # Console output
            RotatingFileHandler(
                LOG_FILE, maxBytes=10**6, backupCount=5
            ),  # Rotating log file
        ],
    )
