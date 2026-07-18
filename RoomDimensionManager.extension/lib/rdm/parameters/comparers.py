# -*- coding: utf-8 -*-
"""
Comparers for the Parameter Management & Cross Check Engine.
Provides tolerance-based mathematical comparisons between calculated dimensions and stored Revit parameters.
"""
from rdm.models.value_objects import Tolerance
from rdm.models.enums import ParameterStatus
from rdm.parameters.models import ParameterComparison

class ToleranceCalculator:
    """Evaluates absolute differences against configured engineering tolerances."""
    
    def __init__(self, tolerance):
        """
        Args:
            tolerance (Tolerance): The absolute allowable deviation (e.g. 0.01 feet).
        """
        self.tolerance = tolerance
        
    def is_within_tolerance(self, calculated, stored):
        """Checks if the difference between two values is acceptable."""
        return self.tolerance.within_tolerance(calculated, stored)

class ParameterComparer:
    """Compares an internally calculated dimension against a raw parameter reading."""
    
    def __init__(self, tolerance_calc):
        self.tolerance_calc = tolerance_calc
        
    def compare(
        self, 
        parameter_name, 
        calculated_internal, 
        stored_internal, 
        param_status) -> ParameterComparison:
        """
        Executes the comparison logic.
        
        Args:
            parameter_name (str): The name of the parameter.
            calculated_internal (float): The newly calculated value in internal units.
            stored_internal (Optional[float]): The existing Revit value in internal units.
            param_status (ParameterStatus): Health of the parameter from the Revit API.
            
        Returns:
            ParameterComparison: Structured domain model containing the comparison results.
        """
        if stored_internal is None or param_status != ParameterStatus.READY:
            return ParameterComparison(
                parameter_name=parameter_name,
                calculated_value=calculated_internal,
                stored_value=None,
                difference=None,
                within_tolerance=False,
                status=param_status
            )
            
        diff = abs(calculated_internal - stored_internal)
        is_ok = self.tolerance_calc.is_within_tolerance(calculated_internal, stored_internal)
        
        return ParameterComparison(
            parameter_name=parameter_name,
            calculated_value=calculated_internal,
            stored_value=stored_internal,
            difference=diff,
            within_tolerance=is_ok,
            status=ParameterStatus.READY
        )
