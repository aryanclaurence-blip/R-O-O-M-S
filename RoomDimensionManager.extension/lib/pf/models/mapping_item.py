# -*- coding: utf-8 -*-
"""Data Binding Model for Mapping Queue DataGrid."""

class MappingItem(object):
    def __init__(self, mapping_obj):
        self.Mapping = mapping_obj
        self.MappingType = mapping_obj.mapping_type
        self.SourceDisplay = mapping_obj.source_param if mapping_obj.mapping_type in ["Parameter Copy", "Find & Replace"] else (
            mapping_obj.static_value if mapping_obj.mapping_type == "Static Value" else mapping_obj.seq_pattern
        )
        self.TargetParameter = mapping_obj.target_param
        self.Status = mapping_obj.status
        
        colors = {
            "VALID": "#008000",
            "WARNING": "#D8A41E",
            "MISSING PARAMETER": "#D83B01",
            "READ ONLY": "#005A9E",
            "ERROR": "#E81123",
            "PENDING": "#555555"
        }
        self.StatusColor = colors.get(self.Status, "#000000")
