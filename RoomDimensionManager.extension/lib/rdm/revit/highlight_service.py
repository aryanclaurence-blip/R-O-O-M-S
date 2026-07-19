# -*- coding: utf-8 -*-
"""Handles Graphic Overrides for rooms in the active view."""
from Autodesk.Revit.DB import Color, OverrideGraphicSettings, Transaction, FilteredElementCollector, FillPatternElement
try:
    from rdm.config import DEVELOPER_DEBUG_MODE
except Exception:
    DEVELOPER_DEBUG_MODE = False

class HighlightService(object):
    COLORS = {
        "PASS": None,
        "FAIL": Color(255, 0, 0),
        "USER REVIEW": Color(255, 165, 0),
        "MISSING PARAMETER": Color(255, 0, 0),
        "READ ONLY": None,
        "GEOMETRY ERROR": Color(255, 0, 255),
        "UPDATED": Color(0, 0, 255)
    }

    _highlighted_elements = []

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
    def clear_previous_overrides(doc, active_view):
        if not HighlightService._highlighted_elements:
            return
        try:
            t = Transaction(doc, "Clear RoomPro Highlights")
            t.Start()
            for eid in HighlightService._highlighted_elements:
                try:
                    ogs = OverrideGraphicSettings()
                    active_view.SetElementOverrides(eid, ogs)
                except Exception:
                    pass
            t.Commit()
            HighlightService._highlighted_elements = []
        except Exception:
            pass

    @staticmethod
    def apply_overrides(doc, active_view, rows):
        HighlightService.clear_previous_overrides(doc, active_view)
        
        solid_fill_id = HighlightService.get_solid_fill_pattern_id(doc)
        if not solid_fill_id:
            raise ValueError("Solid fill pattern not found in document.")

        t = Transaction(doc, "Highlight Rooms")
        t.Start()
        
        success_count = 0
        error_msgs = set()
        
        if DEVELOPER_DEBUG_MODE:
            print("\n======================================================================")
            print("HIGHLIGHT VALIDATION")
            print("======================================================================")
        
        for row in rows:
            color = HighlightService.COLORS.get(row.Result.upper())
            ogs = OverrideGraphicSettings()
            
            if not color:
                if DEVELOPER_DEBUG_MODE:
                    print("Room Number: {}".format(getattr(row, "RoomNumber", "Unknown")))
                    print("Model: {}".format(getattr(row, "DocumentName", "Host")))
                    print("ElementId: {}".format(getattr(row, "ElementId", "Unknown")))
                    print("Graphic Override Applied: No")
                    print("Selection Applied: No")
                    print("Reason if skipped: Result '{}' does not trigger highlight.".format(row.Result))
                    print("-" * 60)
                continue
                
            if getattr(row, "IsLinked", False):
                if DEVELOPER_DEBUG_MODE:
                    print("Room Number: {}".format(getattr(row, "RoomNumber", "Unknown")))
                    print("Model: {}".format(getattr(row, "DocumentName", "Linked")))
                    print("ElementId: {}".format(getattr(row, "ElementId", "Unknown")))
                    print("Graphic Override Applied: No")
                    print("Selection Applied: No")
                    print("Reason if skipped: Elements inside Linked Models cannot be highlighted in the host view.")
                    print("-" * 60)
                error_msgs.add("Elements inside Linked Models cannot be highlighted in the host view.")
                continue
                
            if hasattr(ogs, "SetSurfaceForegroundPatternColor"):
                ogs.SetSurfaceForegroundPatternColor(color)
                ogs.SetSurfaceForegroundPatternId(solid_fill_id)
                ogs.SetSurfaceBackgroundPatternColor(color)
                ogs.SetSurfaceBackgroundPatternId(solid_fill_id)
                ogs.SetProjectionLineColor(color)
                ogs.SetProjectionLineWeight(8)
                ogs.SetSurfaceTransparency(40)
                ogs.SetHalftone(False)
            else:
                # Fallback for older Revit APIs
                ogs.SetProjectionFillColor(color)
                ogs.SetProjectionFillPatternId(solid_fill_id)
                ogs.SetProjectionLineColor(color)
                ogs.SetProjectionLineWeight(8)
                ogs.SetSurfaceTransparency(40)
            
            try:
                active_view.SetElementOverrides(row.Room.Id, ogs)
                HighlightService._highlighted_elements.append(row.Room.Id)
                success_count += 1
                if DEVELOPER_DEBUG_MODE:
                    print("Room Number: {}".format(getattr(row, "RoomNumber", "Unknown")))
                    print("Model: {}".format(getattr(row, "DocumentName", "Host")))
                    print("ElementId: {}".format(getattr(row, "ElementId", "Unknown")))
                    print("Graphic Override Applied: Yes")
                    print("Selection Applied: No")
                    print("Reason if skipped: N/A")
                    print("-" * 60)
            except Exception as e:
                # Attempt Temporary Element Selection fallback if Graphic Overrides completely fail
                selection_applied = "No"
                try:
                    from pyrevit import revit
                    from System.Collections.Generic import List
                    from Autodesk.Revit.DB import ElementId
                    revit.uidoc.Selection.SetElementIds(List[ElementId]([row.Room.Id]))
                    selection_applied = "Yes"
                except:
                    pass
                    
                if DEVELOPER_DEBUG_MODE:
                    print("Room Number: {}".format(getattr(row, "RoomNumber", "Unknown")))
                    print("Model: {}".format(getattr(row, "DocumentName", "Host")))
                    print("ElementId: {}".format(getattr(row, "ElementId", "Unknown")))
                    print("Graphic Override Applied: No")
                    print("Selection Applied: {}".format(selection_applied))
                    print("Reason if skipped: {}".format(str(e)))
                    print("-" * 60)
                error_msgs.add(str(e))
                    
        # Force OST_Rooms category to be visible so overrides are actually seen
        from Autodesk.Revit.DB import BuiltInCategory
        room_cat = doc.Settings.Categories.get_Item(BuiltInCategory.OST_Rooms)
        if room_cat:
            try:
                active_view.SetCategoryHidden(room_cat.Id, False)
            except Exception:
                pass

        t.Commit()
        
        return success_count, list(error_msgs)

    @staticmethod
    def remove_overrides(doc, active_view, rows=None):
        HighlightService.clear_previous_overrides(doc, active_view)
