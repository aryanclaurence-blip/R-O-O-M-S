# -*- coding: utf-8 -*-
"""Revit room collection and boundary access."""
from Autodesk.Revit.DB import BuiltInCategory, FilteredElementCollector
from Autodesk.Revit.DB import SpatialElementBoundaryOptions
from Autodesk.Revit.DB.Architecture import Room
from rdm.utils.compat import GetElementIdValue


class RoomService(object):
    def __init__(self, document):
        self.document = document

    def get_rooms(self, scope, selected_ids=None):
        rooms = []
        selected = set([GetElementIdValue(item) for item in (selected_ids or [])])
        collector = FilteredElementCollector(self.document).OfCategory(BuiltInCategory.OST_Rooms)
        
        # Support for "Current View"
        if scope == "Current View":
            collector = FilteredElementCollector(self.document, self.document.ActiveView.Id).OfCategory(BuiltInCategory.OST_Rooms)
            
        for element in collector:
            if not isinstance(element, Room) or element.Area <= 0 or element.Location is None:
                continue
            if scope == "Selected Rooms" and GetElementIdValue(element.Id) not in selected:
                continue
            rooms.append(element)
        return rooms

    def get_outer_boundary(self, room):
        loops = room.GetBoundarySegments(SpatialElementBoundaryOptions())
        if not loops or not loops[0]:
            raise ValueError("Room is not enclosed.")
        return loops[0]
