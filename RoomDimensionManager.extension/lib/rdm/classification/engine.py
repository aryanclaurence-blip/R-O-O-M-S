# -*- coding: utf-8 -*-
"""
Room Classification Engine.
Evaluates room boundary geometry to assign a strict geometric classification.
"""
from Autodesk.Revit.DB import Line

class RoomClassificationEngine(object):
    """
    Centralized engine for determining room boundary shapes.
    Priority:
    1. Curved Geometry
    2. Perfect Rectangle
    3. Four-Sided Non-Rectangle
    4. Complex Polygon
    """
    
    @classmethod
    def classify(cls, boundary_segments):
        """
        Classifies a list of Autodesk.Revit.DB.BoundarySegment items.
        Returns a string classification.
        """
        if not boundary_segments:
            return "Unknown Geometry"
            
        curves = [seg.GetCurve() for seg in boundary_segments]
        
        # 1. Curved Geometry
        has_curves = False
        for curve in curves:
            if not isinstance(curve, Line):
                has_curves = True
                break
                
        if has_curves:
            return "Curved Geometry"
            
        # All segments are now guaranteed to be straight Lines.
        count = len(curves)
        
        # 4. Complex Polygon (handled at the end as fallback if straight)
        if count != 4:
            return "Complex Polygon"
            
        # Exactly 4 straight lines. Determine if Perfect Rectangle or Non-Rectangle.
        # We need to check if adjacent sides are perpendicular.
        # In a closed 4-sided loop, if 3 consecutive angles are 90 deg, it's a rectangle.
        # We will use dot products.
        
        is_rectangle = True
        tolerance = 1e-5
        
        for i in range(4):
            c1 = curves[i]
            c2 = curves[(i + 1) % 4]
            dir1 = c1.Direction
            dir2 = c2.Direction
            dot_product = abs(dir1.DotProduct(dir2))
            
            # If dot product is not extremely close to 0, it's not perpendicular.
            if dot_product > tolerance:
                is_rectangle = False
                break
                
        if is_rectangle:
            return "Perfect Rectangle"
        else:
            return "Four-Sided Non-Rectangle"

