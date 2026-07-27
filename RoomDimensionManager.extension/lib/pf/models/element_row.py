# -*- coding: utf-8 -*-
"""Data Binding Model for Preview & Execution Results DataGrid."""

class ElementResultRow(object):
    def __init__(self, element, cat_name, source_mapping, target_param, old_val, new_val, status="UPDATED", message="OK"):
        self.Element = element
        self.ElementId = element.Id.IntegerValue if hasattr(element.Id, 'IntegerValue') else element.Id
        self.CategoryName = cat_name
        self.SourceMapping = source_mapping
        self.TargetParameter = target_param
        self.OldValue = old_val
        self.NewValue = new_val
        self.Status = status
        self.Message = message

        colors = {
            "UPDATED": "#008000",
            "PREVIEW": "#0078D7",
            "READ ONLY": "#005A9E",
            "MISSING PARAMETER": "#D83B01",
            "FAILED": "#E81123",
            "ERROR": "#E81123"
        }
        self.StatusColor = colors.get(self.Status, "#000000")
