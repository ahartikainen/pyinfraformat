"""Custom Exceptions for PyInfraformat module."""


class FileExtensionMissingError(Exception):
    """Exception class for missing file extension."""

    pass


class PathNotFoundError(Exception):
    """Exception class for invalid path"""

    pass
