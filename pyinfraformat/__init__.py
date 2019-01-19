# pylint: disable=wildcard-import
"""PyInfraformat, Python library for Finnish infraformat files."""
import logging
from .core import *
from .parser import *
from .io import *
from .plot import *
from .utils import *
from .utils import info_fi as _info_fi


logger = logging.getLogger("pyinfraformat")

if not logging.root.handlers:
    # overwrite the first handler
    # which is always on WARNING -level
    logger.addHandler(logging.NullHandler())
    handler = logging.StreamHandler()
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)


__version__ = "0.1.0a-dev"
__all__ = ["Holes", "from_infraformat", "print_info"]
