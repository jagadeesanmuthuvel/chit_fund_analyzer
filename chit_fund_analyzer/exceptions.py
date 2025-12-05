"""
Custom exceptions for chit fund analysis.

This module defines specific exception classes for different types
of errors that can occur during chit fund analysis.
"""


class ChitFundAnalysisError(Exception):
    """
    Base exception for chit fund analysis errors.
    
    Raised when there are issues with chit fund calculations,
    validation, or data processing.
    """
    
    def __init__(self, message: str, details: dict = None):
        """
        Initialize the exception.
        
        Args:
            message: Error message
            details: Optional dictionary with additional error details
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self) -> str:
        """Return formatted error message."""
        if self.details:
            details_str = ", ".join(f"{k}={v}" for k, v in self.details.items())
            return f"{self.message} (Details: {details_str})"
        return self.message


class ValidationError(ChitFundAnalysisError):
    """
    Exception for data validation errors.
    
    Raised when input data fails validation checks.
    """
    pass


class CalculationError(ChitFundAnalysisError):
    """
    Exception for calculation errors.
    
    Raised when mathematical calculations fail or produce invalid results.
    """
    pass


class ConfigurationError(ChitFundAnalysisError):
    """
    Exception for configuration errors.
    
    Raised when chit fund configuration is invalid or incomplete.
    """
    pass