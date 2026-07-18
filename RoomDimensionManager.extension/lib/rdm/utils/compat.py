# -*- coding: utf-8 -*-
"""Compatibility helpers for pyRevit."""

def GetElementIdValue(element_id):
    """Safely extracts the integer value of an ElementId across Revit versions."""
    try:
        return element_id.Value
    except AttributeError:
        return element_id.IntegerValue
