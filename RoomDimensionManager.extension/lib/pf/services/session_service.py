# -*- coding: utf-8 -*-
"""Session Manager for PARAMS FLOW UI state persistence."""
import os
import json

class SessionService(object):
    _session_file = os.path.expanduser("~/.params_flow_session.json")

    @classmethod
    def save_session(cls, scope, category, mappings_data):
        data = {
            "scope": scope,
            "category": category,
            "mappings": mappings_data
        }
        try:
            with open(cls._session_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass

    @classmethod
    def load_session(cls):
        if not os.path.exists(cls._session_file):
            return None
        try:
            with open(cls._session_file, 'r') as f:
                return json.load(f)
        except Exception:
            return None
