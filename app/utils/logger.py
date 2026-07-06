from pathlib import Path
from logging.handlers import RotatingFileHandler
import os
import logging

# Available uvicorn log levels
from uvicorn.config import LOG_LEVELS


# Create logs directory path object
LOG_DIR = Path('logs')

# Create logs directory if it doesn't exist
LOG_DIR.mkdir(exist_ok=True)

# Full path for log file
LOG_FILE = LOG_DIR / "app.log"

# Get log level from environment variable
# Default = INFO
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()


def get_logger(name: str) -> logging.Logger:
    """
    Create and return a configured logger instance.
    """

    # Create/Get logger with given name
    logger = logging.getLogger(name)

    # Prevent adding duplicate handlers
    # if logger already configured
    if logger.handlers:
        return logger

    # Set logger level
    logger.setLevel(LOG_LEVEL)

    # Log message format
    formatter = logging.Formatter(
        fmt=(
            "%(asctime)s | %(levelname)s | "
            "%(name)s | %(filename)s:%(lineno)d | %(message)s"
        ),
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # ---------------- Console Handler ----------------

    # Print logs to terminal/console
    console_handler = logging.StreamHandler()

    # Apply log format
    console_handler.setFormatter(formatter)

    # ---------------- File Handler ----------------

    # Rotating file handler:
    # Creates new file after size limit reached
    file_handler = RotatingFileHandler(
        filename=LOG_FILE,
        maxBytes=10 * 1024 * 1024,  # 10 MB max size
        backupCount=5,              # Keep last 5 backup files
        encoding="utf-8",
    )

    # Apply formatting to file logs
    file_handler.setFormatter(formatter)

    # ---------------- Add Handlers ----------------

    # Add console output handler
    logger.addHandler(console_handler)

    # Add file logging handler
    logger.addHandler(file_handler)

    # Prevent logs from propagating
    # to root logger multiple times
    logger.propagate = False

    # Return configured logger
    return logger