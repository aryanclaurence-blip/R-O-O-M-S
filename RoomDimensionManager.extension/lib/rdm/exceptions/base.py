# -*- coding: utf-8 -*-
"""IronPython-compatible domain exceptions."""
import datetime
from rdm.exceptions.codes import ErrorCode, ErrorSeverity


class ApplicationException(Exception):
    def __init__(self, message, error_code=ErrorCode.SYS_UNEXPECTED,
                 severity=ErrorSeverity.ERROR, context_data=None):
        Exception.__init__(self, message)
        self.message = message
        self.error_code = error_code
        self.severity = severity
        self.context_data = context_data or {}
        self.timestamp = datetime.datetime.now()

    def __str__(self):
        return "[{0}] {1}".format(self.error_code, self.message)


class RDMBaseException(ApplicationException):
    pass


class GeometryExtractionError(RDMBaseException):
    pass


class ParameterWriteError(RDMBaseException):
    pass
