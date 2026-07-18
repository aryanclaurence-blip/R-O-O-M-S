# -*- coding: utf-8 -*-
"""Application use cases and controllers."""
import logging
from rdm.revit.collectors import RoomCollector
from rdm.core.classification import ClassificationEngine
from rdm.core.calculation import CalculationEngine

logger = logging.getLogger(__name__)

class MainController:
    """Orchestrates the primary Room Dimension Manager workflows."""
    
    def __init__(self):
        self.collector = RoomCollector()
        self.classifier = ClassificationEngine()
        self.calculator = CalculationEngine()
        
    def execute_set_dimensions(self):
        """Run the 'Set Dimensions' workflow."""
        logger.info("Executing Set Dimensions workflow...")
        pass
        
    def execute_cross_check(self):
        """Run the 'Cross Check' workflow."""
        logger.info("Executing Cross Check workflow...")
        pass
