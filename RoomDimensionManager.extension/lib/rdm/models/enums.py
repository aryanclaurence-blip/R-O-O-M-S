# -*- coding: utf-8 -*-
"""
Enumerations for the Room Dimension Manager Domain Models.
Provides strongly typed constants representing specific states and categories.
"""

class ShapeType(object):
    """Architectural classification of a room's geometric footprint."""
    RECTANGLE = "Rectangle"
    SQUARE = "Square"
    ROTATED_RECTANGLE = "Rotated Rectangle"
    PARALLELOGRAM = "Parallelogram"
    TRAPEZOID = "Trapezoid"
    L_SHAPE = "L Shape"
    T_SHAPE = "T Shape"
    U_SHAPE = "U Shape"
    CIRCLE = "Circle"
    ELLIPSE = "Ellipse"
    POLYGON = "Polygon"
    MIXED_GEOMETRY = "Mixed Geometry"
    UNKNOWN_GEOMETRY = "Unknown Geometry"

class ValidationSeverity(object):
    """Severity of a validation result."""
    PASS = "PASS"
    INFO = "INFO"
    WARNING = "WARNING"
    FAILURE = "FAILURE"
    CRITICAL = "CRITICAL"

class OperationStatus(object):
    """Lifecycle status of a command or background operation."""
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

class RoomStatus(object):
    """Geometric and placement state of a Revit Room."""
    VALID = "VALID"
    UNPLACED = "UNPLACED"
    NOT_ENCLOSED = "NOT_ENCLOSED"
    REDUNDANT = "REDUNDANT"
    ZERO_AREA = "ZERO_AREA"

class ParameterStatus(object):
    """Status indicating the health of a target parameter."""
    READY = "READY"
    MISSING = "MISSING"
    READ_ONLY = "READ_ONLY"
    WRONG_TYPE = "WRONG_TYPE"

class ReviewReason(object):
    """Why a room requires manual QA."""
    COMPLEX_SHAPE = "COMPLEX_SHAPE"
    DIMENSION_MISMATCH = "DIMENSION_MISMATCH"
    CALCULATION_ERROR = "CALCULATION_ERROR"
    INVALID_GEOMETRY = "INVALID_GEOMETRY"

class CalculationMode(object):
    """Mode describing how dimensions were resolved."""
    EXACT_ORTHOGONAL = "EXACT_ORTHOGONAL"
    OBB_ALIGNED = "OBB_ALIGNED"
    MIDPOINT_AVERAGE = "MIDPOINT_AVERAGE"
    RADIAL = "RADIAL"
    APPROXIMATED = "APPROXIMATED"

class MeasurementMethod(object):
    """How clear dimensions are extracted."""
    OPPOSITE_PARALLEL = "OPPOSITE_PARALLEL"
    PERPENDICULAR_PROJECTED = "PERPENDICULAR_PROJECTED"
    MINOR_MAJOR_AXIS = "MINOR_MAJOR_AXIS"
    SHORTEST_USABLE = "SHORTEST_USABLE"

class GeometryQuality(object):
    """The precision and cleanliness of the extracted boundary."""
    PERFECT = "PERFECT"
    MICRO_GAPS_HEALED = "MICRO_GAPS_HEALED"
    TESSELLATED_SPLINE = "TESSELLATED_SPLINE"
    DEGRADED = "DEGRADED"

class LogLevel(object):
    """Enterprise logging levels."""
    TRACE = "TRACE"
    DEBUG = "DEBUG"
    INFO = "INFO"
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
    FATAL = "FATAL"

class ReportType(object):
    """Type of report generated."""
    QA_CROSS_CHECK = "QA_CROSS_CHECK"
    SET_DIMENSIONS_SUMMARY = "SET_DIMENSIONS_SUMMARY"
    DIAGNOSTICS = "DIAGNOSTICS"

class OverrideType(object):
    """Style of temporary graphic override."""
    NONE = "NONE"
    FAILED_RED = "FAILED_RED"
    REVIEW_YELLOW = "REVIEW_YELLOW"

class ExportFormat(object):
    """Available formats for external data delivery."""
    CSV = "CSV"
    JSON = "JSON"

class TransactionMode(object):
    """Behavior of Revit transactions during an operation."""
    READ_ONLY = "READ_ONLY"
    SINGLE_BULK = "SINGLE_BULK"
    PER_ELEMENT = "PER_ELEMENT"
