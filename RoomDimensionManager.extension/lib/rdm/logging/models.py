# -*- coding: utf-8 -*-
"""
Models for the Logging framework.
IronPython 2.7 compatible.
"""

class LogContext(object):
    """Execution context injected into log records."""
    def __init__(self, session_id, user_name, machine_name, revit_version, document_path):
        self.session_id = session_id
        self.user_name = user_name
        self.machine_name = machine_name
        self.revit_version = revit_version
        self.document_path = document_path

class LogRecordData(object):
    """Structured data container for a single log event."""
    def __init__(self, timestamp, level, message, module_name, exception=None, context=None):
        self.timestamp = timestamp
        self.level = level
        self.message = message
        self.module_name = module_name
        self.exception = exception
        self.context = context

class LogStatistics(object):
    """Aggregated logging session statistics."""
    def __init__(self, total_errors=0, total_warnings=0, total_info=0):
        self.total_errors = total_errors
        self.total_warnings = total_warnings
        self.total_info = total_info
