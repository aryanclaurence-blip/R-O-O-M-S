# -*- coding: utf-8 -*-
"""Logger and diagnostic utility for PARAMS FLOW."""
import time

class PFExecutionSession(object):
    def __init__(self, operation="Batch Mapping", scope="Current View", category="Rooms"):
        self.operation = operation
        self.scope = scope
        self.category = category
        self.start_time = time.time()
        self.errors = []
        self.warnings = []
        self.logs = []

    def log_info(self, msg):
        self.logs.append("[INFO] {}".format(msg))

    def log_warning(self, msg):
        self.warnings.append(msg)
        self.logs.append("[WARN] {}".format(msg))

    def log_error(self, msg):
        self.errors.append(msg)
        self.logs.append("[ERROR] {}".format(msg))

    def get_duration(self):
        return time.time() - self.start_time
