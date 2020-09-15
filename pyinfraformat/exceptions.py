"""Custom Exceptions for pyinfraformat module."""

__all__ = ["FileExtensionMissingError", "PathNotFoundError"]


class FileExtensionMissingError(Exception):
    """Exception class for missing file extension."""

    def __init__(self, message, errors=None):
        self.message = message
        self.errors = errors
        super().__init__(message)


class PathNotFoundError(Exception):
    """Exception class for invalid path."""

    def __init__(self, message, errors=None):
        self.message = message
        self.errors = errors
        super().__init__(message)
