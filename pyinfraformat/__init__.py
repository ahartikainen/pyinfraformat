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


__version__ = "20.11.20"
__all__ = ["Holes", "from_infraformat", "to_infraformat", "print_info"]
