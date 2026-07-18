# -*- coding: utf-8 -*-
"""Geometry classification engine."""
import logging
from rdm.models.polygon import PolygonModel

logger = logging.getLogger(__name__)

class ClassificationEngine:
    """Classifies polygons into specific architectural shape categories."""
    
    def __init__(self):
        pass
        
    def classify(self, polygon):
        """
        Determine the shape category of a given polygon.
        
        Args:
            polygon (PolygonModel): The extracted room geometry.
            
        Returns:
            str: Shape enum representation (e.g., 'Rectangle').
        """
        logger.debug("Classifying polygon...")
        return "Unknown"
