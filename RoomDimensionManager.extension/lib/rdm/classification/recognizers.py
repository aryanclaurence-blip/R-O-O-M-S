# -*- coding: utf-8 -*-
"""Shape recognizers used by the classification engine."""
from abc import ABC, abstractmethod


class IShapeRecognizer(ABC):
    @abstractmethod
    def recognize(self, polygon):
        pass


class RectangleRecognizer(IShapeRecognizer):
    def __init__(self, tol_service, vec_math):
        self.tol = tol_service
        self.vec_math = vec_math

    def recognize(self, polygon):
        if polygon.inner_loops or polygon.outer_loop.vertex_count != 4:
            return 0.0
        for segment in polygon.outer_loop.segments:
            direction = segment.direction
            if not (self.tol.is_zero(direction.x) or self.tol.is_zero(direction.y)):
                return 0.0
        for index in range(4):
            if not self.vec_math.is_perpendicular(
                    polygon.outer_loop.segments[index].direction,
                    polygon.outer_loop.segments[(index + 1) % 4].direction):
                return 0.0
        return 1.0


class RotatedRectangleRecognizer(IShapeRecognizer):
    def __init__(self, vec_math):
        self.vec_math = vec_math

    def recognize(self, polygon):
        if polygon.inner_loops or polygon.outer_loop.vertex_count != 4:
            return 0.0
        for index in range(4):
            if not self.vec_math.is_perpendicular(
                    polygon.outer_loop.segments[index].direction,
                    polygon.outer_loop.segments[(index + 1) % 4].direction):
                return 0.0
        return 0.95


class LShapeRecognizer(IShapeRecognizer):
    def __init__(self, vec_math):
        self.vec_math = vec_math

    def recognize(self, polygon):
        if polygon.inner_loops or polygon.outer_loop.vertex_count != 6:
            return 0.0
        for index in range(6):
            if not self.vec_math.is_perpendicular(
                    polygon.outer_loop.segments[index].direction,
                    polygon.outer_loop.segments[(index + 1) % 6].direction):
                return 0.0
        return 0.90
