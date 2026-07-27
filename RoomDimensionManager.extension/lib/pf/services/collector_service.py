# -*- coding: utf-8 -*-
"""Collector Service for PARAMS FLOW Discovery Layer."""
from Autodesk.Revit.DB import FilteredElementCollector, ElementId

class PFCollectorService(object):
    def __init__(self, doc, uidoc=None):
        self.doc = doc
        self.uidoc = uidoc

    def GetSelectedElements(self):
        """Returns list of elements currently selected in Revit."""
        if not self.uidoc:
            return []
        try:
            sel_ids = self.uidoc.Selection.GetElementIds()
            elems = []
            for eid in sel_ids:
                e = self.doc.GetElement(eid)
                if e and e.Category:
                    elems.append(e)
            return elems
        except Exception:
            return []

    def GetActiveViewElements(self):
        """Returns non-element-type elements visible in active view."""
        try:
            collector = FilteredElementCollector(self.doc, self.doc.ActiveView.Id).WhereElementIsNotElementType()
            elems = []
            for e in collector:
                if e and e.Category and e.Category.Name:
                    elems.append(e)
            return elems
        except Exception:
            return []

    def GetProjectElements(self):
        """Returns non-element-type elements across entire project."""
        try:
            collector = FilteredElementCollector(self.doc).WhereElementIsNotElementType()
            elems = []
            for e in collector:
                if e and e.Category and e.Category.Name:
                    elems.append(e)
            return elems
        except Exception:
            return []

    def GetElements(self, scope):
        """Dispatches scope string to appropriate collector method."""
        if scope == "Selected Elements":
            return self.GetSelectedElements()
        elif scope == "Current View":
            return self.GetActiveViewElements()
        else: # Entire Project
            return self.GetProjectElements()
