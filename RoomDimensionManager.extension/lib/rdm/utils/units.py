# -*- coding: utf-8 -*-
"""Project unit utilities for robust display formatting and parsing."""
from Autodesk.Revit.DB import UnitFormatUtils
import clr
import System

class UnitHelper(object):
    def __init__(self, doc=None):
        self.doc = doc
        self.units = doc.GetUnits() if doc else None
        self.name = "Project Units"
        
        if doc and self.units:
            try:
                from Autodesk.Revit.DB import SpecTypeId
                self.unit_type = SpecTypeId.Length
            except ImportError:
                from Autodesk.Revit.DB import UnitType
                self.unit_type = UnitType.UT_Length
                
            try:
                from Autodesk.Revit.DB import LabelUtils
                self.name = LabelUtils.GetLabelForUnit(self.units.GetFormatOptions(self.unit_type).GetUnitTypeId())
            except Exception:
                try:
                    from Autodesk.Revit.DB import LabelUtils
                    self.name = LabelUtils.GetLabelForUnit(self.units.GetFormatOptions(self.unit_type).DisplayUnits)
                except Exception:
                    self.name = "Project Units"

    def format_length(self, value):
        """Format an internal decimal foot value into a strictly Project Unit compliant string."""
        if value is None:
            return ""
        if self.doc and self.units:
            return UnitFormatUtils.Format(self.units, self.unit_type, value, False)
        return "{:.3f}".format(value)

    def parse_length(self, val_str):
        """Parse a formatted string into an internal decimal foot double, based on Project Units."""
        if not val_str:
            return None
        if self.doc and self.units:
            parsed = clr.Reference[System.Double]()
            success = UnitFormatUtils.TryParse(self.units, self.unit_type, val_str, parsed)
            if success:
                return parsed.Value
        return None

    def parse_dimension_string(self, input_str):
        """Intelligently parse arbitrary dimension strings into a ParseResult object."""
        from rdm.utils.dimension_parser import SmartDimensionParser
        return SmartDimensionParser.parse(input_str, unit_helper=self)

