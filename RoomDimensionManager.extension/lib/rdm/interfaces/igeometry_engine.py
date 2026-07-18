# -*- coding: utf-8 -*-
"""Interface for geometry extraction and processing."""
from abc import ABC, abstractmethod
from rdm.models.polygon import PolygonModel

class IGeometryEngine(ABC):
    """Abstract interface for the Geometry Engine."""
    
    @abstractmethod
    def extract_polygon(self, spatial_element):
        """Extract boundary segments from a spatial element into a PolygonModel."""
        pass
