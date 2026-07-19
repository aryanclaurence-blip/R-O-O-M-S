# -*- coding: utf-8 -*-
"""Revit room collection and boundary access."""
from Autodesk.Revit.DB import BuiltInCategory, FilteredElementCollector, DesignOption
from Autodesk.Revit.DB import SpatialElementBoundaryOptions
from Autodesk.Revit.DB.Architecture import Room
from rdm.utils.compat import GetElementIdValue


class RoomService(object):
    def __init__(self, document):
        self.document = document

    def get_rooms(self, scope, selected_ids=None):
        rooms = []
        selected = set([GetElementIdValue(item) for item in (selected_ids or [])])
        
        # Diagnostic Tracking as requested
        print("=== ROOM COLLECTION TRACE ({}) ===".format(scope))
        stage2_room_count = 0
        stage3_area_count = 0
        stage4_location_count = 0
        stage5_selection_count = 0

        raw_elements = []

        if scope == "Current View":
            collector = FilteredElementCollector(self.document, self.document.ActiveView.Id).OfCategory(BuiltInCategory.OST_Rooms)
            raw_elements = list(collector)
            print("Stage 1 - Collected from Current View: {}".format(len(raw_elements)))
        else:
            # Entire Project or Selected Rooms
            # Revit API FilteredElementCollector(doc) completely excludes Design Options by default.
            # We must explicitly query the Main Model AND all Design Options.
            
            # 1. Main Model
            main_collector = FilteredElementCollector(self.document).OfCategory(BuiltInCategory.OST_Rooms)
            main_elements = list(main_collector)
            raw_elements.extend(main_elements)
            print("Stage 1a - Collected from Main Model: {}".format(len(main_elements)))
            
            # 2. Design Options
            options = FilteredElementCollector(self.document).OfClass(DesignOption)
            opt_count = 0
            for opt in options:
                opt_collector = FilteredElementCollector(self.document).OfCategory(BuiltInCategory.OST_Rooms).ContainedInDesignOption(opt.Id)
                opt_elements = list(opt_collector)
                raw_elements.extend(opt_elements)
                opt_count += len(opt_elements)
            print("Stage 1b - Collected from Design Options: {}".format(opt_count))
            print("Stage 1c - Total Raw Elements (Main + Options): {}".format(len(raw_elements)))

        for element in raw_elements:
            if not isinstance(element, Room):
                continue
            stage2_room_count += 1
            
            if element.Area <= 0:
                continue
            stage3_area_count += 1
            
            if element.Location is None:
                continue
            stage4_location_count += 1
            
            if scope == "Selected Rooms" and GetElementIdValue(element.Id) not in selected:
                continue
            stage5_selection_count += 1
            
            rooms.append(element)
            
        print("Stage 2 - After Category Filter (isinstance Room): {}".format(stage2_room_count))
        print("Stage 3 - After Placed Filter (Area > 0): {}".format(stage3_area_count))
        print("Stage 4 - After Enclosed Filter (Location is not None): {}".format(stage4_location_count))
        print("Stage 5 - After Selection Scope Filter: {}".format(stage5_selection_count))
        print("Stage 6 - Final Rooms Returned: {}".format(len(rooms)))
        print("==================================================\n")
        
        return rooms

    def get_outer_boundary(self, room):
        loops = room.GetBoundarySegments(SpatialElementBoundaryOptions())
        if not loops or not loops[0]:
            raise ValueError("Room is not enclosed.")
        return loops[0]
