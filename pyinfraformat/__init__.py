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


def print_info(language="fi"):
    """Print out information about the finnish infraformat.

    Currently defined only in Finnish.

    Parameters
    ----------
    language : str, {"fi"}
        short format for language.
    """
    if language.lower() != "fi":
        logger.critical("Only 'fi' info is implemented")
        raise NotImplementedError("Only 'fi' info is implemented")
    print(_info_fi())


__version__ = "0.1.0a-dev"
__all__ = ["Holes", "from_infraformat", "print_info"]
