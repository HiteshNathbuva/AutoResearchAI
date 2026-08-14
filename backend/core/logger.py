"""Centralized application logging.

``get_logger`` is side-effect free so modules can create loggers at import time.
Handlers and levels are attached once, at application startup, by
``configure_logging``.
"""

import logging

PACKAGE_LOGGER = "backend"
LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s %(message)s"


def configure_logging(level: str = "INFO") -> logging.Logger:
    """Attach a single stream handler to the package logger.

    Safe to call more than once: the handler is only added if missing, and the
    level is always refreshed.
    """

    logger = logging.getLogger(PACKAGE_LOGGER)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(LOG_FORMAT))
        logger.addHandler(handler)
        logger.propagate = False
    logger.setLevel(str(level).upper())
    return logger


def get_logger(name: str) -> logging.Logger:
    """Return a logger for ``name`` without configuring global state."""

    return logging.getLogger(name)
