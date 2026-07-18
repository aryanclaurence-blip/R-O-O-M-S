# -*- coding: utf-8 -*-
"""Handles Graphic Overrides for rooms in the active view."""
from Autodesk.Revit.DB import Color, OverrideGraphicSettings, Transaction, FilteredElementCollector, FillPatternElement

class HighlightService(object):
    COLORS = {
        "PASS": None,
        "FAIL": Color(255, 0, 0),
        "USER REVIEW": Color(255, 255, 0),
        "MISSING PARAMETER": Color(255, 165, 0),
        "READ ONLY": Color(0, 0, 255),
        "GEOMETRY ERROR": Color(128, 0, 128)
    }

    @staticmethod
    def get_solid_fill_pattern_id(doc):
        patterns = FilteredElementCollector(doc).OfClass(FillPatternElement).ToElements()
        for fp in patterns:
            try:
                pattern = fp.GetFillPattern()
                if pattern.IsSolidFill:
                    return fp.Id
            except:
                pass
        return None

    @staticmethod
    def apply_overrides(doc, active_view, rows):
        solid_fill_id = HighlightService.get_solid_fill_pattern_id(doc)
        if not solid_fill_id:
            raise ValueError("Solid fill pattern not found in document.")

        t = Transaction(doc, "Highlight Rooms")
        t.Start()
        for row in rows:
            color = HighlightService.COLORS.get(row.Result.upper())
            ogs = OverrideGraphicSettings()
            if color:
                if hasattr(ogs, "SetSurfaceForegroundPatternColor"):
                    ogs.SetSurfaceForegroundPatternColor(color)
                    ogs.SetSurfaceForegroundPatternId(solid_fill_id)
                else:
                    # Fallback for older Revit APIs
                    ogs.SetProjectionFillColor(color)
                    ogs.SetProjectionFillPatternId(solid_fill_id)
            active_view.SetElementOverrides(row.Room.Id, ogs)
        t.Commit()

    @staticmethod
    def remove_overrides(doc, active_view, rows):
        t = Transaction(doc, "Remove Highlights")
        t.Start()
        for row in rows:
            ogs = OverrideGraphicSettings()
            active_view.SetElementOverrides(row.Room.Id, ogs)
        t.Commit()
