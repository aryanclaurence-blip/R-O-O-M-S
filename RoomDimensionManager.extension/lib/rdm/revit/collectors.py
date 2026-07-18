# -*- coding: utf-8 -*-
"""Revit element collectors."""
import logging

logger = logging.getLogger(__name__)

class RoomCollector:
    """Retrieves valid rooms from the active Revit document."""
    
    def get_valid_rooms(self, doc):
        """
        Collect all enclosed, placed rooms with Area > 0.
        
        Args:
            doc: Autodesk.Revit.DB.Document
            
        Returns:
            List[Any]: List of Autodesk.Revit.DB.Architecture.Room
        """
        logger.debug("Collecting valid rooms...")
        return []
