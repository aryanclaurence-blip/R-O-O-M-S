# -*- coding: utf-8 -*-
"""
Strongly typed Configuration Domain Models.
IronPython 2.7 compatible.
"""

class GeometryConfiguration(object):
    def __init__(self, tolerance=0.01, min_area=1.0, ignore_small_segments=True, min_segment_length=0.1):
        self.tolerance = tolerance
        self.min_area = min_area
        self.ignore_small_segments = ignore_small_segments
        self.min_segment_length = min_segment_length

class ClassificationConfiguration(object):
    def __init__(self, confidence_threshold=0.85, allow_mixed_geometry=False):
        self.confidence_threshold = confidence_threshold
        self.allow_mixed_geometry = allow_mixed_geometry

class CalculationConfiguration(object):
    def __init__(self, use_centerline=True, fallback_to_bounding_box=True):
        self.use_centerline = use_centerline
        self.fallback_to_bounding_box = fallback_to_bounding_box

class ParameterConfiguration(object):
    def __init__(self, length_param_name="Length", width_param_name="Width", update_read_only=False):
        self.length_param_name = length_param_name
        self.width_param_name = width_param_name
        self.update_read_only = update_read_only

class LoggingConfiguration(object):
    def __init__(self, log_level="INFO", enable_file_logging=True, max_log_size_mb=10, retain_days=7):
        self.log_level = log_level
        self.enable_file_logging = enable_file_logging
        self.max_log_size_mb = max_log_size_mb
        self.retain_days = retain_days

class ValidationConfiguration(object):
    def __init__(self, strict_mode=True, flag_unclosed_loops=True):
        self.strict_mode = strict_mode
        self.flag_unclosed_loops = flag_unclosed_loops

class ReportingConfiguration(object):
    def __init__(self, default_export_format="CSV", auto_open_reports=True):
        self.default_export_format = default_export_format
        self.auto_open_reports = auto_open_reports

class DeveloperConfiguration(object):
    def __init__(self, debug_mode=False, disable_transactions=False, show_execution_times=False):
        self.debug_mode = debug_mode
        self.disable_transactions = disable_transactions
        self.show_execution_times = show_execution_times

class AppConfiguration(object):
    def __init__(self, geometry=None, classification=None, calculation=None, parameters=None, logging=None, validation=None, reporting=None, developer=None):
        self.geometry = geometry or GeometryConfiguration()
        self.classification = classification or ClassificationConfiguration()
        self.calculation = calculation or CalculationConfiguration()
        self.parameters = parameters or ParameterConfiguration()
        self.logging = logging or LoggingConfiguration()
        self.validation = validation or ValidationConfiguration()
        self.reporting = reporting or ReportingConfiguration()
        self.developer = developer or DeveloperConfiguration()
