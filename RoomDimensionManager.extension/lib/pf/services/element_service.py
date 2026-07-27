# -*- coding: utf-8 -*-
"""Element Service for PARAMS FLOW Discovery Layer."""
from pf.services.collector_service import PFCollectorService
from pf.services.cache_service import PFCacheService

class ElementService(object):
    def __init__(self, doc, uidoc=None):
        self.doc = doc
        self.uidoc = uidoc
        self.collector_service = PFCollectorService(doc, uidoc)

    def get_categories_in_scope(self, scope_name):
        """Returns sorted list of unique category names present in specified scope, with caching."""
        cached = PFCacheService.get_categories(scope_name)
        if cached is not None:
            return cached

        elems = self.collector_service.GetElements(scope_name)
        cats = set()
        for e in elems:
            try:
                if e and e.Category and e.Category.Name:
                    cats.add(e.Category.Name)
            except Exception:
                pass

        result = sorted(cats)
        PFCacheService.set_categories(scope_name, result)
        return result

    def get_elements_in_scope(self, scope_name, category_name=None):
        """Returns elements in scope, optionally filtered by category name, with caching."""
        key = "{}_{}".format(scope_name, category_name if category_name else "ALL")
        cached = PFCacheService.get_elements(key)
        if cached is not None:
            return cached

        all_elems = self.collector_service.GetElements(scope_name)
        if not category_name:
            PFCacheService.set_elements(key, all_elems)
            return all_elems

        filtered = []
        for e in all_elems:
            try:
                if e and e.Category and e.Category.Name == category_name:
                    filtered.append(e)
            except Exception:
                pass

        PFCacheService.set_elements(key, filtered)
        return filtered
