# -*- coding: utf-8 -*-
"""Execution Result Placeholder for PARAMS FLOW."""

class ExecutionResultModel(object):
    def __init__(self, element_id="", category="", status="UPDATED", message="OK"):
        self.ElementId = element_id
        self.CategoryName = category
        self.Status = status
        self.Message = message
