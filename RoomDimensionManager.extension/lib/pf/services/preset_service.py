# -*- coding: utf-8 -*-
"""Preset Service Placeholder for PARAMS FLOW."""
import json

class PresetService(object):
    @staticmethod
    def save(filepath, data):
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

    @staticmethod
    def load(filepath):
        with open(filepath, 'r') as f:
            return json.load(f)
