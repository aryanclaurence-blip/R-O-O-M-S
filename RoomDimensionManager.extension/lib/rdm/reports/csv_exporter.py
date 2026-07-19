# -*- coding: utf-8 -*-
"""CSV report export."""
import csv


def export(path, rows, unit_helper):
    sym = unit_helper.name
    header_length = "Length ({0})".format(sym) if sym else "Length"
    header_width = "Width ({0})".format(sym) if sym else "Width"
    
    with open(path, 'wb') as stream:
        writer = csv.writer(stream)
        writer.writerow(["Model", "Element ID", "Room Number", "Room Name", "Classification", header_length, header_width, "Stored L", "Stored W", "Result"])
        for row in rows:
            writer.writerow([row.DocumentName, row.ElementId, row.RoomNumber, row.RoomName, row.Classification,
                             row.CalculatedLengthDisplay, row.CalculatedWidthDisplay,
                             row.StoredLengthDisplay, row.StoredWidthDisplay, row.Result])
