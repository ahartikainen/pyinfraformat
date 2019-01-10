"""Custom Exceptions for PyInfraformat module."""


class FileExtensionMissingError(Exception):
    """Exception class for missing file extension."""

    def __init__(self, message, errors=None):
        self.message = message
        self.errors = errors
        super(FileExtensionMissingError, self).__init__(message)


class PathNotFoundError(Exception):
    """Exception class for invalid path"""

    self.message = message
    self.errors = errors
    super(PathNotFoundError, self).__init__(message)
