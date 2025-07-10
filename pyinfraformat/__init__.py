"""pyinfraformat, Python library for Finnish infraformat files."""

import logging

from .core import (
    Holes,
    from_gtk_wfs,
    from_infraformat,
    identifiers,
    print_info,
    project_holes,
    to_infraformat,
)
from .exceptions import FileExtensionMissingError, PathNotFoundError
from .plots import plot_hole, plot_map

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


__version__ = "25.7.10"
__all__ = [
    "FileExtensionMissingError",
    "Holes",
    "PathNotFoundError",
    "from_gtk_wfs",
    "from_infraformat",
    "identifiers",
    "plot_hole",
    "plot_map",
    "print_info",
    "project_holes",
    "to_infraformat",
]
