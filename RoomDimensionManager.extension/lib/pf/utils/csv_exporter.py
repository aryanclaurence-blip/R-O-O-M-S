# -*- coding: utf-8 -*-
"""CSV Exporter for PARAMS FLOW mapping execution logs."""
import csv

def export_pf_csv(filepath, rows, session_info=None):
    with open(filepath, 'wb' if str is bytes else 'w') as f:
        writer = csv.writer(f)
        writer.writerow(["Element ID", "Category", "Source Mapping", "Target Parameter", "Old Value", "New Value", "Status", "Message"])
        for row in rows:
            writer.writerow([
                getattr(row, "ElementId", ""),
                getattr(row, "CategoryName", ""),
                getattr(row, "SourceMapping", ""),
                getattr(row, "TargetParameter", ""),
                getattr(row, "OldValue", ""),
                getattr(row, "NewValue", ""),
                getattr(row, "Status", ""),
                getattr(row, "Message", "")
            ])
