# -*- coding: utf-8 -*-
import time
import uuid
from pyrevit import script

class ExecutionSession(object):
    def __init__(self, operation, scope, host_doc_name, linked_models=None):
        self.session_id = str(uuid.uuid4())
        self.start_time = time.time()
        self.end_time = None
        
        self.operation = operation
        self.scope = scope
        self.host_doc_name = host_doc_name
        self.linked_models = linked_models or []
        
        self.logs = []
        self.errors = []
        
        self.timings = {
            "Room Collection": 0,
            "Cross Check": 0,
            "Parameter Writing": 0,
            "Total Execution": 0
        }
        
        self._current_phase_start = 0
        self.log("Execution Session {} Started".format(self.session_id))
        
    def log(self, message):
        timestamp = time.strftime('%H:%M:%S')
        entry = "[{}] {}".format(timestamp, message)
        self.logs.append(entry)
        
    def log_error(self, message):
        timestamp = time.strftime('%H:%M:%S')
        entry = "[{}] ERROR: {}".format(timestamp, message)
        self.logs.append(entry)
        self.errors.append(entry)
        
    def start_timer(self):
        self._current_phase_start = time.time()
        
    def stop_timer(self, phase_name):
        if self._current_phase_start > 0:
            duration = time.time() - self._current_phase_start
            self.timings[phase_name] = duration
            self.log("{} completed in {:.2f}s".format(phase_name, duration))
            self._current_phase_start = 0
            
    def end_session(self):
        self.end_time = time.time()
        self.timings["Total Execution"] = self.end_time - self.start_time
        self.log("Execution Session Completed in {:.2f}s".format(self.timings["Total Execution"]))
        
    def print_to_output(self):
        output = script.get_output()
        output.print_md("---")
        output.print_md("## RoomPro Execution Session: {}".format(self.session_id))
        output.print_md("**Scope:** {} | **Operation:** {}".format(self.scope, self.operation))
        output.print_md("**Host Document:** {}".format(self.host_doc_name))
        if self.linked_models:
            output.print_md("**Linked Models:** {}".format(", ".join(self.linked_models)))
        
        output.print_md("### Execution Log")
        for log_entry in self.logs:
            if "ERROR" in log_entry:
                print("❌ {}".format(log_entry))
            else:
                print("✅ {}".format(log_entry))
                
        output.print_md("### Performance Timings")
        for phase, duration in self.timings.items():
            if duration > 0:
                print("- **{}**: {:.2f} seconds".format(phase, duration))
                
        if self.errors:
            output.print_md("### ⚠️ Errors Encountered ({})".format(len(self.errors)))
            for err in self.errors:
                print(err)
        output.print_md("---")
