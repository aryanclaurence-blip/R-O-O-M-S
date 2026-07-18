# -*- coding: utf-8 -*-
"""
Models for the Room Dimension Calculation Engine.
IronPython 2.7 compatible.
"""

class DimensionResult(object):
    """Represents a calculated 1D spatial dimension."""
    def __init__(self, value, confidence, is_ambiguous):
        self.value = value
        self.confidence = confidence
        self.is_ambiguous = is_ambiguous

class CalculationStatistics(object):
    """Metadata regarding the calculation execution."""
    def __init__(self, calculation_mode, execution_time_ms, aspect_ratio, area, perimeter, longest_edge, shortest_edge):
        self.calculation_mode = calculation_mode
        self.execution_time_ms = execution_time_ms
        self.aspect_ratio = aspect_ratio
        self.area = area
        self.perimeter = perimeter
        self.longest_edge = longest_edge
        self.shortest_edge = shortest_edge

class RoomCalculationResult(object):
    """The final calculated engineering dimensions for a room."""
    def __init__(self, length, width, statistics, requires_review, review_reasons=None, validation_messages=None):
        self.length = length
        self.width = width
        self.statistics = statistics
        self.requires_review = requires_review
        self.review_reasons = review_reasons or []
        self.validation_messages = validation_messages or []
    
    @property
    def is_successful(self):
        """Returns True if calculations yielded valid non-zero results."""
        return self.length.value.internal_value > 0 and self.width.value.internal_value > 0
