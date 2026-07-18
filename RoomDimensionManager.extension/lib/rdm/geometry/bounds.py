# -*- coding: utf-8 -*-
"""Geometry extraction for Revit room boundary loops."""


class RoomDimensions(object):
    def __init__(self, length, width, classification):
        self.length = length
        self.width = width
        self.classification = classification


def calculate_from_boundary(segments):
    points = []
    for segment in segments:
        curve = segment.GetCurve()
        points.append(curve.GetEndPoint(0))
        points.append(curve.GetEndPoint(1))
    if len(points) < 3:
        raise ValueError("Room boundary has insufficient points.")
    xs = [point.X for point in points]
    ys = [point.Y for point in points]
    x_size = max(xs) - min(xs)
    y_size = max(ys) - min(ys)
    if x_size <= 0 or y_size <= 0:
        raise ValueError("Room boundary has no measurable extent.")
    classification = "Rectangle" if len(segments) == 4 else "Polygon"
    return RoomDimensions(max(x_size, y_size), min(x_size, y_size), classification)
