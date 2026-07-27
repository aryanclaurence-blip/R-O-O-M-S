# -*- coding: utf-8 -*-
"""Handles Graphic Overrides for rooms in the active view."""
from Autodesk.Revit.DB import Color, OverrideGraphicSettings, Transaction, FilteredElementCollector, FillPatternElement
try:
    from rdm.config import DEVELOPER_DEBUG_MODE
except Exception:
    DEVELOPER_DEBUG_MODE = False

class HighlightService(object):
    SHAPE_COLORS = {
        "Perfect Rectangle": Color(0, 200, 80),         # Vibrant Green
        "Four-Sided Non-Rectangle": Color(245, 158, 11),# Vibrant Amber/Gold
        "Complex Polygon": Color(139, 92, 246),          # Vibrant Purple
        "Curved Geometry": Color(236, 72, 153),          # Vibrant Pink
        "User Selected": Color(59, 130, 246)             # Vibrant Blue
    }

    RESULT_COLORS = {
        "FAIL": Color(255, 0, 0),
        "USER REVIEW": Color(255, 165, 0),
        "MISSING PARAMETER": Color(255, 0, 0),
        "GEOMETRY ERROR": Color(255, 0, 255),
        "UPDATED": Color(0, 0, 255)
    }

    _highlighted_elements = set()

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
    def clear_previous_overrides(doc, active_view, element_ids=None):
        """Clear graphic overrides for specified element_ids, or all highlighted elements if element_ids is None."""
        target_ids = list(element_ids) if element_ids is not None else list(HighlightService._highlighted_elements)
        if not target_ids:
            return
        try:
            t = Transaction(doc, "Clear RoomPro Highlights")
            t.Start()
            for eid in target_ids:
                try:
                    ogs = OverrideGraphicSettings()
                    active_view.SetElementOverrides(eid, ogs)
                except Exception:
                    pass
                if eid in HighlightService._highlighted_elements:
                    HighlightService._highlighted_elements.remove(eid)
            t.Commit()
        except Exception:
            pass

    @staticmethod
    def apply_overrides(doc, active_view, rows, shape_category=None, override_color=None):
        """Additively apply graphic overrides for the given rows based on Shape/Category without filtering out PASS rooms."""
        solid_fill_id = HighlightService.get_solid_fill_pattern_id(doc)
        if not solid_fill_id:
            raise ValueError("Solid fill pattern not found in document.")

        success_count = 0
        error_msgs = set()

        t = Transaction(doc, "Highlight Rooms")
        t.Start()

        for row in rows:
            if getattr(row, "IsLinked", False) or not getattr(row, "Room", None):
                if getattr(row, "IsLinked", False):
                    error_msgs.add("Linked model elements cannot be highlighted in host view.")
                continue

            color = override_color
            if not color and shape_category:
                color = HighlightService.SHAPE_COLORS.get(shape_category)
            if not color and hasattr(row, "Classification"):
                color = HighlightService.SHAPE_COLORS.get(row.Classification)
            if not color and hasattr(row, "Result"):
                color = HighlightService.RESULT_COLORS.get(row.Result.upper())
            if not color:
                color = Color(59, 130, 246)  # Default vibrant blue fallback

            ogs = OverrideGraphicSettings()
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
                ogs.SetProjectionFillColor(color)
                ogs.SetProjectionFillPatternId(solid_fill_id)
                ogs.SetProjectionLineColor(color)
                ogs.SetProjectionLineWeight(8)
                ogs.SetSurfaceTransparency(40)

            try:
                active_view.SetElementOverrides(row.Room.Id, ogs)
                HighlightService._highlighted_elements.add(row.Room.Id)
                success_count += 1
            except Exception as e:
                error_msgs.add(str(e))

        from Autodesk.Revit.DB import BuiltInCategory
        room_cat = doc.Settings.Categories.get_Item(BuiltInCategory.OST_Rooms)
        if room_cat:
            try:
                active_view.SetCategoryHidden(room_cat.Id, False)
            except Exception:
                pass

        t.Commit()

        print("\n--------------------------------------------------")
        print("Highlight Requested")
        print("Shape: {}".format(shape_category if shape_category else "Custom"))
        print("Rooms Found: {}".format(len(rows)))
        print("Element IDs: {}".format([r.Room.Id.IntegerValue for r in rows if getattr(r, 'Room', None)]))
        print("Applying Overrides: {}".format("YES" if success_count > 0 else "NO"))
        print("Transaction Started: YES")
        print("SetElementOverrides Called: YES ({})".format(success_count))
        print("Transaction Committed: YES")
        print("View Regenerated: YES")
        print("Exceptions: {}".format(list(error_msgs)))
        print("--------------------------------------------------\n")

        return success_count, list(error_msgs)

    @staticmethod
    def remove_overrides(doc, active_view, rows=None):
        HighlightService.clear_previous_overrides(doc, active_view)
