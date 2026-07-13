"""
Centralized logging configuration.
Sets up structured, readable logs for the whole application.
"""

import logging
import sys


def configure_logging(debug: bool = False) -> None:
    """
    Configures the root logger with a consistent format across the app.

    Format includes: timestamp, log level, logger name (module), and message.
    This makes it easy to trace which part of the system logged what.
    """
    log_level = logging.DEBUG if debug else logging.INFO

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Avoid duplicate handlers if this is called more than once (e.g. with --reload)
    root_logger.handlers.clear()
    root_logger.addHandler(handler)

    # Quiet down noisy third-party loggers
    logging.getLogger("watchfiles").setLevel(logging.WARNING)