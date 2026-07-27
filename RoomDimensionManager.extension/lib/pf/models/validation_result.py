# -*- coding: utf-8 -*-
"""Validation Result Placeholder for PARAMS FLOW."""

class ValidationResultModel(object):
    def __init__(self, mapping_name="", status="VALID", message="OK"):
        self.MappingName = mapping_name
        self.Status = status
        self.Message = message
