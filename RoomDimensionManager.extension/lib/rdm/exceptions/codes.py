# -*- coding: utf-8 -*-
"""
Error Codes for the Room Dimension Manager.
Provides structured and unique identifiers for all exceptions.
"""

class ErrorSeverity(object):
    """Defines the severity level of an error."""
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
    FATAL = "FATAL"

class ErrorCode(object):
    """
    Structured unique error codes for all system exceptions.
    Prefix mapping:
        SYS - System / Unexpected
        CFG - Configuration
        VAL - Validation
        GEO - Geometry
        RMM - Room Processing
        PAR - Parameters
        CAL - Calculation
        TRX - Transactions
        REP - Reporting
        UI  - User Interface
    """
    # System Errors (999)
    SYS_UNEXPECTED = "SYS-999"
    SYS_TIMEOUT = "SYS-998"
    SYS_DEPENDENCY = "SYS-997"
    SYS_CANCELLED = "SYS-996"

    # Configuration Errors (001-099)
    CFG_MISSING = "CFG-001"
    CFG_INVALID = "CFG-002"
    CFG_CORRUPT = "CFG-003"
    
    # Validation Errors (100-199)
    VAL_NULL = "VAL-101"
    VAL_EMPTY = "VAL-102"
    VAL_TYPE = "VAL-103"
    VAL_RANGE = "VAL-104"
    VAL_DUPLICATE = "VAL-105"

    # Geometry Errors (200-299)
    GEO_EXTRACTION_FAILED = "GEO-201"
    GEO_INVALID_POLYGON = "GEO-202"
    GEO_UNCLOSED_LOOP = "GEO-203"

    # Room Errors (300-399)
    RMM_NOT_ENCLOSED = "RMM-301"
    RMM_UNPLACED = "RMM-302"
    RMM_ZERO_AREA = "RMM-303"

    # Parameter Errors (400-499)
    PAR_MISSING = "PAR-401"
    PAR_READ_ONLY = "PAR-402"
    PAR_INVALID_TYPE = "PAR-403"

    # Calculation Errors (500-599)
    CAL_MATH_DOMAIN = "CAL-501"
    CAL_DIVISION_ZERO = "CAL-502"

    # Transaction Errors (600-699)
    TRX_FAILED = "TRX-601"
    TRX_ROLLBACK_FAILED = "TRX-602"

    # Reporting Errors (700-799)
    REP_WRITE_FAILED = "REP-701"
    REP_FILE_LOCKED = "REP-702"

    # UI Errors (800-899)
    UI_BINDING_FAILED = "UI-801"
    UI_WINDOW_LOAD_FAILED = "UI-802"
