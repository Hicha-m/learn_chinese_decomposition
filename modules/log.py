import logging


LOGGER_NAME = "learn-app"
_logger = logging.getLogger(LOGGER_NAME)


def log_show(level=logging.DEBUG,name=LOGGER_NAME):
    logging.getLogger(name).setLevel(level)


def info(message, logger=_logger):
    """Log an info level message."""
    logger.info(message)


def debug(message, logger=_logger):
    """Log a debug level message."""
    logger.debug(message)


def warning(message, logger=_logger):
    """Log a warning level message."""
    logger.warning(message)


def error(message, logger=_logger):
    """Log an error level message."""
    logger.error(message)


def critical(message, logger=_logger):
    """Log a critical level message."""
    logger.critical(message)


logging.basicConfig(
level=logging.INFO,
format="%(levelname)s:%(name)s:%(message)s",
force=True
)

log_show()