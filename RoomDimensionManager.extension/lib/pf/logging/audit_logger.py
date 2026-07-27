# -*- coding: utf-8 -*-
"""Audit Logger for PARAMS FLOW Enterprise Logging."""
import os
import json
import time

class PFAuditLogger(object):
    _log_file = os.path.expanduser("~/.params_flow_audit.log")

    @classmethod
    def log_event(cls, event_type, details=None):
        entry = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "event_type": event_type,
            "details": details or {}
        }
        try:
            with open(cls._log_file, 'a') as f:
                f.write(json.dumps(entry) + "\n")
        except Exception:
            pass
