# -*- coding: utf-8 -*-
"""JSON Preset import/export manager for PARAMS FLOW."""
import json
import time

class PresetService(object):
    @staticmethod
    def save_preset(filepath, mappings_data, project_name="Revit Model"):
        """Save mapping queue list of dicts to JSON file."""
        data = {
            "Tool": "PARAMS FLOW",
            "Version": "1.0.0",
            "SchemaVersion": "1.0",
            "Timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "Project": project_name,
            "Mappings": mappings_data
        }
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

    @staticmethod
    def load_preset(filepath):
        """Load mapping queue list of dicts from JSON file with schema validation."""
        with open(filepath, 'r') as f:
            data = json.load(f)

        if not isinstance(data, dict):
            raise ValueError("Invalid preset file format.")

        tool_name = data.get("Tool", "")
        if tool_name != "PARAMS FLOW":
            raise ValueError("Unrecognized preset file: Tool name is '{}'".format(tool_name))

        mappings = data.get("Mappings", [])
        if not isinstance(mappings, list):
            raise ValueError("Preset file contains no valid mappings list.")

        return mappings
