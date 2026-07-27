# -*- coding: utf-8 -*-
"""Element and Category discovery service for PARAMS FLOW."""
from Autodesk.Revit.DB import FilteredElementCollector, BuiltInCategory, ElementId

class ElementService(object):
    def __init__(self, doc, uidoc=None):
        self.doc = doc
        self.uidoc = uidoc

    def get_categories_in_scope(self, scope_name):
        """Returns sorted list of category names present in the specified scope."""
        cats = set()
        elements = self.get_elements_in_scope(scope_name, category_name=None)
        for elem in elements:
            try:
                if elem and elem.Category and elem.Category.Name:
                    cats.add(elem.Category.Name)
            except Exception:
                pass
        return sorted(cats)

    def get_elements_in_scope(self, scope_name, category_name=None):
        """Returns list of elements in scope, optionally filtered by category name."""
        if scope_name == "Selected Elements":
            if not self.uidoc:
                return []
            sel_ids = self.uidoc.Selection.GetElementIds()
            elems = []
            for eid in sel_ids:
                e = self.doc.GetElement(eid)
                if e and e.Category:
                    if not category_name or e.Category.Name == category_name:
                        elems.append(e)
            return elems

        collector = None
        if scope_name == "Current View":
            collector = FilteredElementCollector(self.doc, self.doc.ActiveView.Id).WhereElementIsNotElementType()
        else: # Entire Project
            collector = FilteredElementCollector(self.doc).WhereElementIsNotElementType()

        elems = []
        for e in collector:
            try:
                if e and e.Category and e.Category.Name:
                    if not category_name or e.Category.Name == category_name:
                        elems.append(e)
            except Exception:
                pass
        return elems
