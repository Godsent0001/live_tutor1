# app/core/logger.py

import logging
import sys
from datetime import datetime


class Logger:
    """
    Simple structured logger for backend tracing.
    """

    def __init__(self, name: str = "live_tutor"):

        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)

        handler = logging.StreamHandler(sys.stdout)

        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        handler.setFormatter(formatter)

        if not self.logger.handlers:
            self.logger.addHandler(handler)

    # ----------------------------
    # INFO
    # ----------------------------
    def info(self, message: str):

        self.logger.info(message)

    # ----------------------------
    # ERROR
    # ----------------------------
    def error(self, message: str):

        self.logger.error(message)

    # ----------------------------
    # WARNING
    # ----------------------------
    def warning(self, message: str):

        self.logger.warning(message)

    # ----------------------------
    # DEBUG
    # ----------------------------
    def debug(self, message: str):

        self.logger.debug(message)


# Global logger instance
logger = Logger()