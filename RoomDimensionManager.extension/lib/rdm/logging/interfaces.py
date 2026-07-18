# -*- coding: utf-8 -*-
"""
Abstract interfaces for the Enterprise Logging Framework.
Ensures strong typing and clean dependency injection.
"""
from abc import ABC, abstractmethod
from rdm.logging.models import LogEntry, LogContext

class ILogFormatter(ABC):
    """Abstract interface for formatting log entries into strings."""
    @abstractmethod
    def format(self, entry):
        pass

class ILogWriter(ABC):
    """Abstract interface for writing logs to a destination."""
    @abstractmethod
    def write(self, entry, formatted_message):
        pass
        
    @abstractmethod
    def flush(self):
        pass

class ILogRepository(ABC):
    """Abstract interface for querying historical logs (future feature)."""
    @abstractmethod
    def query(self, session_id):
        pass

class ILogger(ABC):
    """Base interface for all specialized loggers."""
    
    @abstractmethod
    def log(self, level, message, **kwargs):
        pass

    @abstractmethod
    def trace(self, message, **kwargs):
        pass

    @abstractmethod
    def debug(self, message, **kwargs):
        pass

    @abstractmethod
    def info(self, message, **kwargs):
        pass
        
    @abstractmethod
    def success(self, message, **kwargs):
        pass

    @abstractmethod
    def warning(self, message, **kwargs):
        pass

    @abstractmethod
    def error(self, message, **kwargs):
        pass

    @abstractmethod
    def critical(self, message, **kwargs):
        pass

    @abstractmethod
    def fatal(self, message, **kwargs):
        pass
