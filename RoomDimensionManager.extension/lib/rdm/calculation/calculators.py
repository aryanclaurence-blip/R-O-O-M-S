# -*- coding: utf-8 -*-
"""IronPython-safe strategies for deriving rectangular room dimensions."""
from abc import ABC, abstractmethod
from rdm.models.value_objects import Distance, Percentage
from rdm.calculation.models import DimensionResult


class IDimensionCalculator(ABC):
    @abstractmethod
    def calculate(self, polygon, internal_unit):
        pass


class RectangleCalculator(IDimensionCalculator):
    def __init__(self, tol_service):
        self.tol = tol_service

    def calculate(self, polygon, internal_unit):
        outer = polygon.outer_loop
        if outer.vertex_count != 4:
            empty = DimensionResult(Distance(0, internal_unit), Percentage(0), True)
            return empty, empty

        first = outer.segments[0].length
        second = outer.segments[1].length
        factor = internal_unit.conversion_factor_to_internal
        length = DimensionResult(Distance(max(first, second) / factor, internal_unit), Percentage(100), False)
        width = DimensionResult(Distance(min(first, second) / factor, internal_unit), Percentage(100), False)
        return length, width


class SquareCalculator(RectangleCalculator):
    def calculate(self, polygon, internal_unit):
        length, width = RectangleCalculator.calculate(self, polygon, internal_unit)
        average = (length.value.internal_value + width.value.internal_value) / 2.0
        result = DimensionResult(Distance(average / internal_unit.conversion_factor_to_internal, internal_unit), Percentage(100), False)
        return result, result
