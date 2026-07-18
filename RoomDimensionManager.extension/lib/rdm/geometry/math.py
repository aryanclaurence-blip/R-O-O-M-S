# -*- coding: utf-8 -*-
"""
Mathematical Services for the Computational Geometry Engine.
Provides robust numerical operations, intersection detection, and tolerance checks.
"""
import math
from rdm.models.geometry import Point2D, Vector2D, LineSegment
from rdm.models.value_objects import Tolerance

class ToleranceService:
    """Provides numerical stability checks and floating-point comparisons."""
    
    def __init__(self, default_tolerance= 0.001):
        self._tol = Tolerance(default_tolerance)
        
    def is_zero(self, value):
        """Check if a value is effectively zero."""
        return self._tol.within_tolerance(value, 0.0)
        
    def are_equal(self, a, b):
        """Check if two floats are equal within tolerance."""
        return self._tol.within_tolerance(a, b)
        
    def points_equal(self, p1, p2):
        """Check if two points occupy the same spatial coordinate."""
        return p1.is_almost_equal(p2, self._tol)

class DistanceService:
    """Calculates spatial distances between geometric entities."""
    
    def distance_point_to_line(self, point, line):
        """
        Calculate the shortest perpendicular distance from a point to a line segment.
        If the projection falls outside the segment, returns the distance to the closest endpoint.
        """
        l2 = (line.start.x - line.end.x)**2 + (line.start.y - line.end.y)**2
        if l2 == 0:
            return point.distance_to(line.start)
            
        t = max(0, min(1, ((point.x - line.start.x) * (line.end.x - line.start.x) + 
                           (point.y - line.start.y) * (line.end.y - line.start.y)) / l2))
        
        projection = Point2D(line.start.x + t * (line.end.x - line.start.x),
                             line.start.y + t * (line.end.y - line.start.y))
        return point.distance_to(projection)

class IntersectionService:
    """Calculates intersections between geometric entities."""
    
    def __init__(self, tol_service):
        self.tol = tol_service
        
    def segment_intersection(self, s1, s2):
        """
        Calculate the 2D intersection point of two line segments.
        Returns None if they do not intersect or are collinear.
        """
        p = s1.start
        r = Vector2D(s1.end.x - s1.start.x, s1.end.y - s1.start.y)
        q = s2.start
        s = Vector2D(s2.end.x - s2.start.x, s2.end.y - s2.start.y)
        
        r_cross_s = r.cross(s)
        q_minus_p = Vector2D(q.x - p.x, q.y - p.y)
        
        if self.tol.is_zero(r_cross_s):
            # Collinear or parallel
            return None
            
        t = q_minus_p.cross(s) / r_cross_s
        u = q_minus_p.cross(r) / r_cross_s
        
        if 0.0 <= t <= 1.0 and 0.0 <= u <= 1.0:
            return Point2D(p.x + t * r.x, p.y + t * r.y)
            
        return None

class VectorMathService:
    """Advanced vector operations for angular extraction."""
    
    def __init__(self, tol_service):
        self.tol = tol_service
        
    def angle_between(self, v1, v2):
        """
        Calculate the smallest angle between two vectors in radians [0, pi].
        """
        dot = v1.dot(v2)
        det = v1.x * v2.y - v1.y * v2.x
        return math.atan2(abs(det), dot)
        
    def is_parallel(self, v1, v2):
        """Check if two vectors are parallel."""
        return self.tol.is_zero(v1.cross(v2))
        
    def is_perpendicular(self, v1, v2):
        """Check if two vectors are strictly perpendicular."""
        return self.tol.is_zero(v1.dot(v2))
