# -*- coding: utf-8 -*-
"""History Manager for PARAMS FLOW execution records."""
import os
import json
import time

class HistoryService(object):
    _history_file = os.path.expanduser("~/.params_flow_history.json")

    @classmethod
    def record_execution(cls, project_name, mappings_count, processed_count, updated_count, duration):
        entry = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "project": project_name or "Active Revit Document",
            "mappings_count": mappings_count,
            "processed_count": processed_count,
            "updated_count": updated_count,
            "duration_seconds": round(duration, 2)
        }
        history = cls.get_history()
        history.insert(0, entry)
        history = history[:50]

        try:
            with open(cls._history_file, 'w') as f:
                json.dump(history, f, indent=2)
        except Exception:
            pass

    @classmethod
    def get_history(cls):
        if not os.path.exists(cls._history_file):
            return []
        try:
            with open(cls._history_file, 'r') as f:
                return json.load(f)
        except Exception:
            return []
