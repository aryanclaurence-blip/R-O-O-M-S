# -*- coding: utf-8 -*-
"""Dimension calculation engine."""
import logging
from rdm.models.polygon import PolygonModel

logger = logging.getLogger(__name__)

class CalculationEngine:
    """Calculates dimensions from classified room geometry."""
    
    def __init__(self):
        pass
        
    def calculate_dimensions(self, polygon, shape_type):
        """
        Calculate the primary Length and Width of the polygon.
        
        Args:
            polygon (PolygonModel): The extracted room geometry.
            shape_type (str): The shape classification.
            
        Returns:
            Tuple[float, float]: (Length, Width)
        """
        logger.debug("Calculating dimensions for {0}...".format(shape_type))
        return (0.0, 0.0)
