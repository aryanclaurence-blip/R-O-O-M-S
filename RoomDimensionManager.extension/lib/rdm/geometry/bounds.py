# -*- coding: utf-8 -*-
"""Geometry extraction for Revit room boundary loops."""
from Autodesk.Revit.DB import Line, XYZ

class RoomDimensions(object):
    def __init__(self, length, width, classification):
        self.length = length
        self.width = width
        self.classification = classification


def calculate_from_boundary(segments, length_rule="Largest", width_rule="Smallest"):
    curves = [seg.GetCurve() for seg in segments]
    
    # 1. Extract all tessellated points to perfectly encapsulate arcs and splines
    points = []
    directions = []
    
    for curve in curves:
        points.extend(curve.Tessellate())
        if isinstance(curve, Line):
            directions.append(curve.Direction.Normalize())

    if len(points) < 3:
        raise ValueError("Room boundary has insufficient points.")

    # 2. If no straight lines exist, fallback to global X/Y
    if not directions:
        directions.append(XYZ(1, 0, 0))

    min_area = float('inf')
    best_x_size = 0.0
    best_y_size = 0.0

    # 3. Minimum Area Bounding Rectangle Algorithm
    # Test each straight segment direction as the primary axis
    for dir_x in directions:
        dir_y = XYZ(-dir_x.Y, dir_x.X, 0).Normalize()
        
        xs = [pt.DotProduct(dir_x) for pt in points]
        ys = [pt.DotProduct(dir_y) for pt in points]
        
        x_size = max(xs) - min(xs)
        y_size = max(ys) - min(ys)
        
        area = x_size * y_size
        if area < min_area:
            min_area = area
            best_x_size = x_size
            best_y_size = y_size

    if best_x_size <= 0 or best_y_size <= 0:
        raise ValueError("Room boundary has no measurable extent.")

    largest = max(best_x_size, best_y_size)
    smallest = min(best_x_size, best_y_size)

    if length_rule == "Smallest":
        length = smallest
    elif length_rule == "Average":
        length = (best_x_size + best_y_size) / 2.0
    else:
        length = largest

    if width_rule == "Largest":
        width = largest
    elif width_rule == "Average":
        width = (best_x_size + best_y_size) / 2.0
    else:
        width = smallest
        
    # Strictly respect the existing robust classification engine
    from rdm.classification.engine import RoomClassificationEngine
    classification = RoomClassificationEngine.classify(segments)
    
    return RoomDimensions(length, width, classification)
