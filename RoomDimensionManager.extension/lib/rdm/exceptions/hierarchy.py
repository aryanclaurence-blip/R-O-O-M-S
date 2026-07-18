# -*- coding: utf-8 -*-
"""
Exception Hierarchy for the Room Dimension Manager.
Defines specific exception classes that inherit from ApplicationException.
"""
from rdm.exceptions.base import ApplicationException
from rdm.exceptions.codes import ErrorCode, ErrorSeverity

class ConfigurationException(ApplicationException):
    """Raised when configuration loading or validation fails."""
    def __init__(self, message, error_code= ErrorCode.CFG_INVALID, **kwargs):
        super().__init__(message, error_code, **kwargs)

class ValidationException(ApplicationException):
    """Raised when input parameters, configurations, or states fail validation."""
    def __init__(self, message, error_code= ErrorCode.VAL_TYPE, **kwargs):
        super().__init__(message, error_code, **kwargs)

class GeometryException(ApplicationException):
    """Raised during mathematical processing of curves and polygons."""
    def __init__(self, message, error_code= ErrorCode.GEO_EXTRACTION_FAILED, **kwargs):
        super().__init__(message, error_code, **kwargs)

class RoomException(ApplicationException):
    """Raised when encountering invalid room states in Revit."""
    def __init__(self, message, error_code= ErrorCode.RMM_NOT_ENCLOSED, **kwargs):
        super().__init__(message, error_code, **kwargs)

class ParameterException(ApplicationException):
    """Raised when reading or writing parameters fails."""
    def __init__(self, message, error_code= ErrorCode.PAR_MISSING, **kwargs):
        super().__init__(message, error_code, **kwargs)

class CalculationException(ApplicationException):
    """Raised during dimension calculations (e.g. math domain errors)."""
    def __init__(self, message, error_code= ErrorCode.CAL_MATH_DOMAIN, **kwargs):
        super().__init__(message, error_code, **kwargs)

class ReportingException(ApplicationException):
    """Raised when file I/O operations fail during reporting."""
    def __init__(self, message, error_code= ErrorCode.REP_WRITE_FAILED, **kwargs):
        super().__init__(message, error_code, **kwargs)

class TransactionException(ApplicationException):
    """Raised when a Revit Transaction fails or rollback fails."""
    def __init__(self, message, error_code= ErrorCode.TRX_FAILED, **kwargs):
        super().__init__(message, error_code, severity=ErrorSeverity.CRITICAL, **kwargs)

class UIException(ApplicationException):
    """Raised when the WPF Window fails to initialize or bind."""
    def __init__(self, message, error_code= ErrorCode.UI_WINDOW_LOAD_FAILED, **kwargs):
        super().__init__(message, error_code, **kwargs)

class UserCancelledException(ApplicationException):
    """Raised to gracefully exit when a user cancels an operation."""
    def __init__(self, message= "User cancelled the operation.", **kwargs):
        super().__init__(message, ErrorCode.SYS_CANCELLED, severity=ErrorSeverity.INFO, **kwargs)
