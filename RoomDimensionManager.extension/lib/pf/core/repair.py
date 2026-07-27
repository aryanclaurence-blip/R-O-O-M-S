# -*- coding: utf-8 -*-
"""Repair Engine for PARAMS FLOW."""

class RepairSuggestion(object):
    def __init__(self, mapping, issue_type, suggestion_msg):
        self.mapping = mapping
        self.issue_type = issue_type
        self.suggestion_msg = suggestion_msg

class RepairEngine(object):
    def __init__(self, doc):
        self.doc = doc

    def analyze(self, validation_result):
        """Analyze validation result and return repair suggestions."""
        status = validation_result.status
        mapping = validation_result.mapping

        if status == "MISSING PARAMETER":
            return RepairSuggestion(
                mapping,
                "MISSING PARAMETER",
                "Parameter '{}' does not exist on target category. Add Shared/Project parameter or select an existing parameter.".format(mapping.target_param)
            )
        elif status == "READ ONLY":
            return RepairSuggestion(
                mapping,
                "READ ONLY",
                "Parameter '{}' is Built-In / Read-Only. Select a writable parameter (e.g. Comments, Mark, Shared Parameter).".format(mapping.target_param)
            )
        elif status == "WARNING":
            return RepairSuggestion(
                mapping,
                "PARTIAL WARNING",
                "Some elements have missing or read-only parameters. Execution will update valid elements and skip read-only/missing elements safely."
            )
        return None
