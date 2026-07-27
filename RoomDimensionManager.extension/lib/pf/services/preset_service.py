# -*- coding: utf-8 -*-
"""JSON Preset import/export manager with Schema 1.1 Versioning for PARAMS FLOW."""
import json
import time

class PresetService(object):
    @staticmethod
    def save_preset(filepath, mappings_data, project_name="Revit Model", doc_guid=None):
        """Save mapping queue list of dicts to JSON file with Schema 1.1 persistent metadata."""
        data = {
            "Tool": "PARAMS FLOW",
            "Version": "1.0.0",
            "SchemaVersion": "1.1",
            "MinSupportedVersion": "1.0.0",
            "Timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "ProjectName": project_name,
            "ProjectGUID": str(doc_guid) if doc_guid else "N/A",
            "Mappings": mappings_data
        }
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

    @staticmethod
    def load_preset(filepath):
        """Load mapping queue list of dicts from JSON file with schema 1.1 validation and upgrade."""
        with open(filepath, 'r') as f:
            data = json.load(f)

        if not isinstance(data, dict):
            raise ValueError("Invalid preset file format.")

        tool_name = data.get("Tool", "")
        if tool_name != "PARAMS FLOW":
            raise ValueError("Unrecognized preset file: Tool name is '{}'".format(tool_name))

        schema_ver = data.get("SchemaVersion", "1.0")
        mappings = data.get("Mappings", [])
        if not isinstance(mappings, list):
            raise ValueError("Preset file contains no valid mappings list.")

        # Seamless migration for legacy Schema 1.0 presets
        if schema_ver == "1.0":
            for m in mappings:
                m.setdefault("source_cat", m.get("target_cat", "Rooms"))
                m.setdefault("health_status", "COMPATIBLE")

        return mappings
