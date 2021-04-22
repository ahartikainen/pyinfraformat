# pylint: disable=wildcard-import
"""pyinfraformat, Python library for Finnish infraformat files."""
import logging

from .core import *
from .exceptions import *
from .plots import *

logger = logging.getLogger("pyinfraformat")

if not logging.root.handlers:
    # overwrite the first handler
    # which is always on WARNING -level
    logger.addHandler(logging.NullHandler())
    handler = logging.StreamHandler()
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)


def set_logger_level(level):
    """Set level for pyinfraformat logger, level must be an int (0-50) or a str."""
    logger.setLevel(level)


def log_to_file(filename):
    """Replace logging handler to log to file."""
    file_handler = logging.FileHandler(filename, encoding="utf-8")
    logger.handlers = [file_handler]


__version__ = "21.4.22"
__all__ = ["Holes", "from_infraformat", "to_infraformat", "print_info"]
