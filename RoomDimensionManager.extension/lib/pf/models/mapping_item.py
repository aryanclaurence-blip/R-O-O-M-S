# -*- coding: utf-8 -*-
"""Data Binding Model for Mapping Queue DataGrid."""

class MappingItem(object):
    def __init__(self, mapping_obj, order=1):
        self.Mapping = mapping_obj
        self.Order = order
        self.Enabled = getattr(mapping_obj, 'enabled', True)
        self.MappingType = mapping_obj.mapping_type
        self.SourceDisplay = mapping_obj.source_param if mapping_obj.mapping_type in ["Parameter Copy", "Find & Replace", "Prefix", "Suffix"] else (
            mapping_obj.static_value if mapping_obj.mapping_type == "Static Value" else mapping_obj.seq_pattern
        )
        self.TargetParameter = mapping_obj.target_param
        self.TargetCategory = getattr(mapping_obj, 'target_cat', 'Rooms')
        
        if not self.Enabled:
            self.Status = "Disabled"
            self.StatusColor = "#888888"
        else:
            self.Status = mapping_obj.status
            colors = {
                "Ready": "#008000",
                "VALID": "#008000",
                "Warning": "#D8A41E",
                "WARNING": "#D8A41E",
                "Error": "#E81123",
                "ERROR": "#E81123",
                "Not Validated": "#0078D7",
                "Disabled": "#888888"
            }
            self.StatusColor = colors.get(self.Status, "#555555")
