# -*- coding: utf-8 -*-
"""
Models for the Reporting & Export Engine.
IronPython 2.7 compatible.
"""
from rdm.models.enums import ExportFormat

class ExportConfiguration(object):
    """Settings controlling how and where reports are generated."""
    def __init__(self, destination_path, export_format=ExportFormat.CSV, overwrite_existing=True, include_summary=True, delimiter=",", encoding="utf-8"):
        self.destination_path = destination_path
        self.export_format = export_format
        self.overwrite_existing = overwrite_existing
        self.include_summary = include_summary
        self.delimiter = delimiter
        self.encoding = encoding

class ReportRow(object):
    """A single atomic record representing one processed room."""
    def __init__(self, room_id, room_number, room_name, level, department, classification, area, perimeter, calculated_length, calculated_width, stored_length, stored_width, length_difference, width_difference, is_pass, requires_review, review_reasons=None, execution_time_ms=0.0, validation_messages=None):
        self.room_id = room_id
        self.room_number = room_number
        self.room_name = room_name
        self.level = level
        self.department = department
        self.classification = classification
        self.area = area
        self.perimeter = perimeter
        self.calculated_length = calculated_length
        self.calculated_width = calculated_width
        self.stored_length = stored_length
        self.stored_width = stored_width
        self.length_difference = length_difference
        self.width_difference = width_difference
        self.is_pass = is_pass
        self.requires_review = requires_review
        self.review_reasons = review_reasons or []
        self.execution_time_ms = execution_time_ms
        self.validation_messages = validation_messages or []

class ReportStatistics(object):
    """Aggregated numerical statistics for an entire report."""
    def __init__(self, total_rooms=0, processed_rooms=0, passed=0, failed=0, warnings=0, user_review=0, skipped=0, errors=0, average_runtime_ms=0.0, total_runtime_ms=0.0, average_width=0.0, average_length=0.0):
        self.total_rooms = total_rooms
        self.processed_rooms = processed_rooms
        self.passed = passed
        self.failed = failed
        self.warnings = warnings
        self.user_review = user_review
        self.skipped = skipped
        self.errors = errors
        self.average_runtime_ms = average_runtime_ms
        self.total_runtime_ms = total_runtime_ms
        self.average_width = average_width
        self.average_length = average_length

class ReportModel(object):
    """The master container for a generated report."""
    def __init__(self, project_name, model_name, date_generated, revit_version, plugin_version, statistics, rows=None):
        self.project_name = project_name
        self.model_name = model_name
        self.date_generated = date_generated
        self.revit_version = revit_version
        self.plugin_version = plugin_version
        self.statistics = statistics
        self.rows = rows or []
