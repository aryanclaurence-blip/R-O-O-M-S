# -*- coding: utf-8 -*-
import os

def trace_collection(doc, filepath):
    with open(filepath, 'w') as f:
        try:
            from Autodesk.Revit.DB import FilteredElementCollector, BuiltInCategory
            from Autodesk.Revit.DB.Architecture import Room
            
            f.write("=== ROOM COLLECTION TRACE ===\n")
            
            collector = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Rooms)
            all_elements = list(collector)
            f.write("Collected from document (OST_Rooms): {}\n".format(len(all_elements)))
            
            is_room_count = 0
            area_count = 0
            location_count = 0
            
            for el in all_elements:
                if isinstance(el, Room):
                    is_room_count += 1
                    if el.Area > 0:
                        area_count += 1
                        if el.Location is not None:
                            location_count += 1
                            
            f.write("After isinstance(Room): {}\n".format(is_room_count))
            f.write("After Area > 0: {}\n".format(area_count))
            f.write("After Location is not None: {}\n".format(location_count))
            
            # Now let's try Current View
            active_view = doc.ActiveView
            if active_view:
                view_col = FilteredElementCollector(doc, active_view.Id).OfCategory(BuiltInCategory.OST_Rooms)
                view_elements = list(view_col)
                f.write("\nCollected from Current View: {}\n".format(len(view_elements)))
                
                v_is_room = 0
                v_area = 0
                v_loc = 0
                for el in view_elements:
                    if isinstance(el, Room):
                        v_is_room += 1
                        if el.Area > 0:
                            v_area += 1
                            if el.Location is not None:
                                v_loc += 1
                f.write("View - After isinstance(Room): {}\n".format(v_is_room))
                f.write("View - After Area > 0: {}\n".format(v_area))
                f.write("View - After Location is not None: {}\n".format(v_loc))
                
        except Exception as e:
            f.write("ERROR: {}\n".format(e))
