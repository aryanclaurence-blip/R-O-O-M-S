# -*- coding: utf-8 -*-
"""JSON Preset import/export manager for PARAMS FLOW."""
import json

class PresetService(object):
    @staticmethod
    def save_preset(filepath, mappings_data):
        """Save mapping queue list of dicts to JSON file."""
        data = {
            "tool": "PARAMS FLOW",
            "version": "1.0.0",
            "mappings": mappings_data
        }
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

    @staticmethod
    def load_preset(filepath):
        """Load mapping queue list of dicts from JSON file."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        return data.get("mappings", [])
