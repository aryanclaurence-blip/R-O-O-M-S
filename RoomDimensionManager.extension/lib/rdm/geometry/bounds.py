# -*- coding: utf-8 -*-
"""Geometry extraction for Revit room boundary loops."""


class RoomDimensions(object):
    def __init__(self, length, width, classification):
        self.length = length
        self.width = width
        self.classification = classification


def calculate_from_boundary(segments, length_rule="Largest", width_rule="Smallest"):
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
    largest = max(x_size, y_size)
    smallest = min(x_size, y_size)
    if length_rule == "Smallest":
        length = smallest
    elif length_rule == "Average":
        length = (x_size + y_size) / 2.0
    else:
        length = largest

    if width_rule == "Largest":
        width = largest
    elif width_rule == "Average":
        width = (x_size + y_size) / 2.0
    else:
        width = smallest
        
    classification = "Rectangle" if len(segments) == 4 else "Polygon"
    return RoomDimensions(length, width, classification)
