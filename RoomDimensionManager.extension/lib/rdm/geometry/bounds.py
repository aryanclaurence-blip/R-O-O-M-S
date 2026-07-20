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
        if isinstance(curve, Line):
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
        # Group lines by orientation
        groups = []
        for line in lines:
            v = line.Direction.Normalize()
            length = line.Length
            placed = False
            for g in groups:
                if abs(v.DotProduct(g['dir'])) > 0.99:
                    g['lengths'].append(length)
                    placed = True
                    break
            if not placed:
                groups.append({'dir': v, 'lengths': [length]})
        
        # Sort groups by total length to find the primary axes
        groups.sort(key=lambda x: sum(x['lengths']), reverse=True)
        
        # We need exactly two orthogonal dominant groups to proceed with this algorithm
        if len(groups) >= 2 and abs(groups[0]['dir'].DotProduct(groups[1]['dir'])) < 0.05:
            x_walls = groups[0]['lengths']
            y_walls = groups[1]['lengths']
            
            final_length = apply_rule(x_walls, length_rule)
            final_width = apply_rule(y_walls, width_rule)
        else:
            raise ValueError("Opposite Wall Average requires at least two orthogonal wall directions.")

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
