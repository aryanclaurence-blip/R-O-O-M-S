# -*- coding: utf-8 -*-
"""
Models for the Parameter Management & Cross Check Engine.
IronPython 2.7 compatible.
"""
from rdm.models.enums import ParameterStatus

class ParameterResult(object):
    """The result of reading a parameter from an element."""
    def __init__(self, parameter_name, status, stored_value_internal=None, is_read_only=False):
        self.parameter_name = parameter_name
        self.status = status
        self.stored_value_internal = stored_value_internal
        self.is_read_only = is_read_only

class ParameterComparison(object):
    """The result of comparing a calculated dimension against a stored parameter."""
    def __init__(self, parameter_name, calculated_value, stored_value, difference, within_tolerance, status):
        self.parameter_name = parameter_name
        self.calculated_value = calculated_value
        self.stored_value = stored_value
        self.difference = difference
        self.within_tolerance = within_tolerance
        self.status = status
    
class CrossCheckResult(object):
    """The complete audit record for a single room."""
    def __init__(self, room_id, room_number, room_name, length_comparison, width_comparison, is_pass, requires_review, review_reasons=None, validation_messages=None):
        self.room_id = room_id
        self.room_number = room_number
        self.room_name = room_name
        self.length_comparison = length_comparison
        self.width_comparison = width_comparison
        self.is_pass = is_pass
        self.requires_review = requires_review
        self.review_reasons = review_reasons or []
        self.validation_messages = validation_messages or []

class ParameterWriteResult(object):
    """The result of attempting to write calculated dimensions to parameters."""
    def __init__(self, room_id, success, error_message=None):
        self.room_id = room_id
        self.success = success
        self.error_message = error_message
