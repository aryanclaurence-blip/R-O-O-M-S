# -*- coding: utf-8 -*-
"""Geometry extraction for Revit room boundary loops."""
from Autodesk.Revit.DB import Line, XYZ

class RoomDimensions(object):
    def __init__(self, length, width, classification):
        self.length = length
        self.width = width
        self.classification = classification


def calculate_from_boundary(segments, algorithm="Opposite Wall Average (Default)", length_rule="Largest", width_rule="Smallest"):
    curves = [seg.GetCurve() for seg in segments]
    
    # 1. Extract all tessellated points to perfectly encapsulate arcs and splines
    points = []
    directions = []
    lines = []
    
    for curve in curves:
        points.extend(curve.Tessellate())
        if hasattr(curve, "Direction"):
            directions.append(curve.Direction.Normalize())
            lines.append(curve)

    if len(points) < 3:
        raise ValueError("Room boundary has insufficient points.")

    # 2. If no straight lines exist, fallback to global X/Y
    if not directions:
        directions.append(XYZ(1, 0, 0))

    # Helper function to apply UI rules
    def apply_rule(values, rule):
        if not values:
            return 0.0
        if rule == "Smallest":
            return min(values)
        elif rule == "Average":
            return sum(values) / len(values)
        else:  # Largest
            return max(values)

    # ALGORITHM 1: OPPOSITE WALL AVERAGE
    if "Opposite Wall" in algorithm:
        if not lines:
            raise ValueError("Opposite Wall Average requires at least one straight wall.")
            
        # 1. Establish the dominant axis (X) using the longest straight wall
        primary_line = max(lines, key=lambda l: l.Length)
        x_dir = primary_line.Direction.Normalize()
        
        x_walls = []
        y_walls = []
        
        # 2. Classify every straight wall into the X or Y bucket using a 45-degree split
        for line in lines:
            v = line.Direction.Normalize()
            # cos(45 degrees) is approximately 0.707
            if abs(v.DotProduct(x_dir)) >= 0.707:
                x_walls.append(line.Length)
            else:
                y_walls.append(line.Length)
                
        final_length = apply_rule(x_walls, length_rule)
        final_width = apply_rule(y_walls, width_rule)

        from rdm.classification.engine import RoomClassificationEngine
        classification = RoomClassificationEngine.classify(segments)
        return RoomDimensions(final_length, final_width, classification)

    # ALGORITHM 2: MINIMUM AREA BOUNDING RECTANGLE (MABR)
    min_area = float('inf')
    best_x_size = 0.0
    best_y_size = 0.0
    
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

    # Apply Length and Width rules to the two candidate MABR dimensions
    final_length = apply_rule([best_x_size, best_y_size], length_rule)
    final_width = apply_rule([best_x_size, best_y_size], width_rule)
        
    # Strictly respect the existing robust classification engine
    from rdm.classification.engine import RoomClassificationEngine
    classification = RoomClassificationEngine.classify(segments)
    
    return RoomDimensions(final_length, final_width, classification)
