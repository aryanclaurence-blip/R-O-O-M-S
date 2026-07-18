# -*- coding: utf-8 -*-
"""
Value Objects for the Room Dimension Manager.
IronPython 2.7 compatible.
"""

class Distance(object):
    """Immutable representation of a spatial distance."""
    def __init__(self, internal_value, unit):
        self.internal_value = internal_value
        self.unit = unit

class Percentage(object):
    """Immutable representation of a percentage value (0.0 to 100.0)."""
    def __init__(self, value):
        self.value = max(0.0, min(100.0, float(value)))

class Identifier(object):
    """Immutable representation of a domain entity identifier."""
    def __init__(self, value):
        self.value = value
        
    def __eq__(self, other):
        if not isinstance(other, Identifier):
            return False
        return self.value == other.value
        
    def __hash__(self):
        return hash(self.value)

class Color(object):
    """Immutable representation of an RGB Color."""
    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b

class LengthUnit(object):
    """Definition of a specific length unit."""
    def __init__(self, name, symbol, conversion_factor_to_internal):
        self.name = name
        self.symbol = symbol
        self.conversion_factor_to_internal = conversion_factor_to_internal

class Tolerance(object):
    """A business rule for comparing two dimensions."""
    def __init__(self, absolute_distance):
        self.absolute_distance = absolute_distance
        
    def within_tolerance(self, val1, val2):
        if val1 is None or val2 is None:
            return False
        return abs(val1 - val2) <= self.absolute_distance
