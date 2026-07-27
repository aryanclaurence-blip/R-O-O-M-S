# -*- coding: utf-8 -*-
"""Preview Row Placeholder for PARAMS FLOW."""

class PreviewRowModel(object):
    def __init__(self, element_id="", category="", source_mapping="", target_param="", old_val="", new_val="", status="PREVIEW"):
        self.ElementId = element_id
        self.CategoryName = category
        self.SourceMapping = source_mapping
        self.TargetParameter = target_param
        self.OldValue = old_val
        self.NewValue = new_val
        self.Status = status
        self.StatusColor = "#0078D7"
