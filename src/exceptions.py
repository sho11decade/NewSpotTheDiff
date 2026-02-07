"""Custom exception classes."""


class ValidationError(Exception):
    """Raised when input validation fails."""


class ProcessingError(Exception):
    """Raised when AI processing fails."""


class ResourceExhaustedError(Exception):
    """Raised when server resources are exhausted."""
