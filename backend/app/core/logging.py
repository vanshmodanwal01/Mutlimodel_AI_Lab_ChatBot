import logging
import sys


def setup_logging(level: str = "INFO") -> logging.Logger:
    """Configures structured application logging without exposing sensitive data."""
    log_format = "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s"
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    # Configure root logger
    logging.basicConfig(
        level=numeric_level,
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

    logger = logging.getLogger("mindbridge")
    logger.setLevel(numeric_level)
    return logger


logger = setup_logging()
