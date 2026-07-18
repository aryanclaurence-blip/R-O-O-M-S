# -*- coding: utf-8 -*-
"""CSV report export."""
import csv


def export(path, rows):
    with open(path, 'wb') as stream:
        writer = csv.writer(stream)
        writer.writerow(["Room Number", "Room Name", "Classification", "Length (ft)", "Width (ft)", "Stored Length", "Stored Width", "Result"])
        for row in rows:
            writer.writerow([row.RoomNumber, row.RoomName, row.Classification,
                             row.CalculatedLength, row.CalculatedWidth,
                             row.StoredLength, row.StoredWidth, row.Result])
