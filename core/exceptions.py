class BusinessAutomationError(Exception):
    """Base exception for the application."""


class ValidationError(BusinessAutomationError):
    """Raised when input data validation fails."""


class FileReadError(BusinessAutomationError):
    """Raised when an input file cannot be read."""


class ExportError(BusinessAutomationError):
    """Raised when output generation fails."""
