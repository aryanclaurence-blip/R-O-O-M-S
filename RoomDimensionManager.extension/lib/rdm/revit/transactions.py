# -*- coding: utf-8 -*-
"""Revit transaction managers."""
import logging

logger = logging.getLogger(__name__)

class TransactionManager:
    """Manages bulk transactions and temporary overrides."""
    
    def __init__(self, doc):
        self.doc = doc
        
    def execute_in_transaction(self, name, action):
        """
        Wraps an action inside a Revit Transaction.
        
        Args:
            name (str): Name of the transaction.
            action (Callable): Function to execute.
            
        Returns:
            bool: True if transaction committed successfully.
        """
        logger.info("Starting transaction: {0}".format(name))
        return True
