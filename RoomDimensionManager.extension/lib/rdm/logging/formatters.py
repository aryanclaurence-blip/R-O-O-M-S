# -*- coding: utf-8 -*-
"""
Log Formatters for the Enterprise Logging Framework.
"""
from rdm.logging.models import LogEntry
from rdm.logging.interfaces import ILogFormatter

class StandardLogFormatter(ILogFormatter):
    """
    Formats a LogEntry into a human-readable text string.
    """
    
    def format(self, entry):
        """
        Converts the LogEntry to a standard string.
        
        Args:
            entry (LogEntry): The log entry to format.
            
        Returns:
            str: Formatted log string.
        """
        timestamp_str = entry.timestamp.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        
        # Build core message
        formatted = (
            "[{0}] ".format(timestamp_str)
            "[{0}] ".format(entry.level.ljust(8))
            "[{0}] ".format(entry.context.thread_id)
            "[{0}] ".format(entry.context.correlation_id[:8])
            "[{0}.{1}.{2}] ".format(entry.module_name, entry.class_name, entry.method_name)
            "- {0}".format(entry.message)
        )
        
        # Append execution time if available
        if entry.execution_time_ms is not None:
            formatted += " [Duration: {0}ms]".format(entry.execution_time_ms:.2f)
            
        # Append exception details if present
        if entry.exception_details:
            formatted += "\nException Details:\n{0}".format(entry.exception_details)
            
        # Append additional data
        if entry.additional_data:
            formatted += "\nData: {0}".format(entry.additional_data)
            
        return formatted

class JSONLogFormatter(ILogFormatter):
    """
    Formats a LogEntry into a JSON-serialized string (Future capability).
    """
    
    def format(self, entry):
        """
        Converts the LogEntry to JSON.
        
        Args:
            entry (LogEntry): The log entry to format.
            
        Returns:
            str: JSON formatted string.
        """
        import json
        
        data = {
            "timestamp": entry.timestamp.isoformat(),
            "level": entry.level,
            "message": entry.message,
            "session_id": entry.context.session_id,
            "correlation_id": entry.context.correlation_id,
            "module": entry.module_name,
            "class": entry.class_name,
            "method": entry.method_name,
            "execution_time_ms": entry.execution_time_ms,
            "additional_data": entry.additional_data
        }
        
        if entry.exception_details= entry.exception_details
            
        return json.dumps(data)
