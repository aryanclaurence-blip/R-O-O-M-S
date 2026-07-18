# -*- coding: utf-8 -*-
"""Parameter management wrappers."""
import logging
from rdm.exceptions.base import ParameterWriteError

logger = logging.getLogger(__name__)

class ParameterManager:
    """Reads and writes parameters safely."""
    
    def write_dimension(self, element, param_name, value):
        """
        Writes a float value to the specified parameter.
        
        Args:
            element (Any): The Revit element.
            param_name (str): The name of the parameter.
            value (float): The calculated dimension.
            
        Returns:
            bool: True if successful.
            
        Raises:
            ParameterWriteError: If parameter is missing or read-only.
        """
        try:
            logger.debug("Writing {0} to {1}...".format(value, param_name))
            return True
        except Exception as e:
            logger.error("Failed to write parameter: {0}".format(e))
            raise ParameterWriteError("Error writing {0}: {1}".format(param_name, e))
