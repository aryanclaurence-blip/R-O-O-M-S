# -*- coding: utf-8 -*-
"""
Parameter Services for the Revit API Layer.
Provides safe abstraction for reading and writing Revit parameters.
"""
import logging
from rdm.revit.interfaces import IParameterService
from rdm.models.value_objects import Identifier
from rdm.exceptions.hierarchy import ParameterException, ErrorCode

logger = logging.getLogger(__name__)

class ParameterService(IParameterService):
    """
    Implementation of IParameterService.
    Abstracts the Revit Parameter API, handling storage types and read-only checks.
    """
    
    def __init__(self, doc):
        """
        Initialize the ParameterService.
        
        Args:
            doc (Autodesk.Revit.DB.Document): The active Revit document.
        """
        self._doc = doc

    def _get_element(self, element_id):
        try:
            from Autodesk.Revit.DB import ElementId
            return self._doc.GetElement(ElementId(int(element_id.value)))
        except ImportError:
            return None

    def write_dimension(self, element_id, param_name, value):
        """
        Safely writes a float value to the targeted parameter.
        
        Args:
            element_id (Identifier): Domain ID of the target element.
            param_name (str): Name of the parameter.
            value (float): The dimension to write.
            
        Returns:
            bool: True if successful.
            
        Raises:
            ParameterException: If parameter is missing, read-only, or wrong type.
        """
        element = self._get_element(element_id)
        if not element:
            raise ParameterException("Element {0} not found.".format(element_id.value), error_code=ErrorCode.PAR_MISSING)
            
        param = element.LookupParameter(param_name)
        if not param:
            raise ParameterException("Parameter '{0}' not found.".format(param_name), error_code=ErrorCode.PAR_MISSING)
            
        if param.IsReadOnly:
            raise ParameterException("Parameter '{0}' is read-only.".format(param_name), error_code=ErrorCode.PAR_READ_ONLY)
            
        try:
            from Autodesk.Revit.DB import StorageType
            if param.StorageType == StorageType.Double:
                param.Set(value)
            elif param.StorageType == StorageType.String:
                param.Set(str(value))
            else:
                raise ParameterException("Unsupported StorageType for '{0}'.".format(param_name), error_code=ErrorCode.PAR_INVALID_TYPE)
                
            logger.debug("Successfully wrote {0} to '{1}' on element {2}.".format(value, param_name, element_id.value))
            return True
            
        except Exception as e:
            raise ParameterException("Failed to write parameter '{0}': {1}".format(param_name, e), error_code=ErrorCode.SYS_UNEXPECTED)

    def read_dimension(self, element_id, param_name):
        """
        Reads a float dimension from the targeted parameter.
        
        Args:
            element_id (Identifier): Domain ID of the element.
            param_name (str): Name of the parameter.
            
        Returns:
            Optional[float]: The parsed float value, or None if empty.
        """
        element = self._get_element(element_id)
        if not element:
            return None
            
        param = element.LookupParameter(param_name)
        if not param or not param.HasValue:
            return None
            
        try:
            from Autodesk.Revit.DB import StorageType
            if param.StorageType == StorageType.Double:
                return param.AsDouble()
            elif param.StorageType == StorageType.String= param.AsString()
                return float(val) if val else None
            elif param.StorageType == StorageType.Integer:
                return float(param.AsInteger())
            return None
        except ValueError:
            logger.warning("Failed to parse float from parameter '{0}'.".format(param_name))
            return None
