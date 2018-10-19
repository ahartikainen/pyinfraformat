from .core import Infraformat
from .parser import read
from .utils import info_fi as _info_fi


def print_info(language="fi"):
    if language.lower() != "fi":
        raise NotImplementedError("Only 'fi' info is implemented")
    print(_info_fi())

__version__ = "0.1.0a"
__all__ = {"Infraformat", "read", "print_info"}
