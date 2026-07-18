# -*- coding: utf-8 -*-
"""CSV and JSON report exporters."""
import csv
import json
import os


class CSVExporter(object):
    def export(self, report, config):
        directory = os.path.dirname(config.destination_path)
        if directory and not os.path.isdir(directory):
            os.makedirs(directory)
        with open(config.destination_path, 'wb') as stream:
            writer = csv.writer(stream, delimiter=config.delimiter)
            writer.writerow(["Room ID", "Number", "Name", "Classification", "Calculated Length", "Calculated Width", "Pass"])
            for row in report.rows:
                writer.writerow([row.room_id.value, row.room_number, row.room_name,
                                 row.classification, row.calculated_length,
                                 row.calculated_width, row.is_pass])
        return config.destination_path


class JSONExporter(object):
    def export(self, report, config):
        directory = os.path.dirname(config.destination_path)
        if directory and not os.path.isdir(directory):
            os.makedirs(directory)
        rows = []
        for row in report.rows:
            rows.append(dict(row.__dict__, room_id=row.room_id.value))
        with open(config.destination_path, 'w') as stream:
            json.dump({'rows': rows}, stream, indent=2)
        return config.destination_path
