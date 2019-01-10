# pylint: disable=wildcard-import,invalid-name,wrong-import-position
from .core import *
from .parser import *
from .io import *
from .plot import *
from .utils import *
import logging

logger = logging.getLogger("pyinfraformat")

if not logging.root.handlers:
    handler = logging.StreamHandler()
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)


def print_info(language="fi"):
    if language.lower() != "fi":
        logger.critical("Only 'fi' info is implemented")
        raise NotImplementedError("Only 'fi' info is implemented")
    print(_info_fi())


__version__ = "0.1.0a-dev"
__all__ = ["Holes", "from_infraformat", "print_info"]
