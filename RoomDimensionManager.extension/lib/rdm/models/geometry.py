# -*- coding: utf-8 -*-
"""Pure geometry value objects.  Kept deliberately IronPython 2.7 safe."""
import math


class Point2D(object):
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)

    def distance_to(self, other):
        dx = self.x - other.x
        dy = self.y - other.y
        return math.sqrt(dx * dx + dy * dy)

    def is_almost_equal(self, other, tolerance):
        return self.distance_to(other) <= tolerance.absolute_distance


class Vector2D(object):
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)

    @property
    def magnitude(self):
        return math.sqrt(self.x * self.x + self.y * self.y)

    def normalize(self):
        magnitude = self.magnitude
        if magnitude == 0:
            return Vector2D(0, 0)
        return Vector2D(self.x / magnitude, self.y / magnitude)

    def dot(self, other):
        return self.x * other.x + self.y * other.y

    def cross(self, other):
        return self.x * other.y - self.y * other.x

    dot_product = dot
    cross_product = cross


class LineSegment(object):
    def __init__(self, start, end):
        self.start = start
        self.end = end

    @property
    def length(self):
        return self.start.distance_to(self.end)

    @property
    def direction(self):
        dx = self.end.x - self.start.x
        dy = self.end.y - self.start.y
        return Vector2D(dx, dy).normalize()


class PolygonLoop(object):
    def __init__(self, segments):
        self.segments = segments or []

    @property
    def vertex_count(self):
        return len(self.segments)


class RoomPolygon(object):
    def __init__(self, outer_loop, inner_loops=None):
        self.outer_loop = outer_loop
        self.inner_loops = inner_loops or []
