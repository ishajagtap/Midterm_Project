# app/exceptions.py
class CalculationError(Exception):
    """Base class for calculation errors."""

class DivisionByZeroError(CalculationError):
    """Raised when dividing by zero."""

class InvalidInputError(CalculationError):
    """Raised for invalid user input."""

class ConfigError(Exception):
    """Configuration error."""

class ValidationError(Exception):
    """Raised when user input fails validation (range, type, etc.)."""
    pass
class OperationError(CalculationError):
    """Raised when an operation cannot be performed (domain errors, unsupported, etc.)."""

class PersistenceError(CalculationError):
    """Raised for history save/load (CSV) errors."""