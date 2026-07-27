# -*- coding: utf-8 -*-
"""Cache Service for PARAMS FLOW Discovery Layer."""

class PFCacheService(object):
    _categories_cache = {}
    _elements_cache = {}
    _parameters_cache = {}

    @classmethod
    def get_categories(cls, scope_key):
        return cls._categories_cache.get(scope_key)

    @classmethod
    def set_categories(cls, scope_key, categories):
        cls._categories_cache[scope_key] = categories

    @classmethod
    def get_elements(cls, key):
        return cls._elements_cache.get(key)

    @classmethod
    def set_elements(cls, key, elements):
        cls._elements_cache[key] = elements

    @classmethod
    def get_parameters(cls, cat_key):
        return cls._parameters_cache.get(cat_key)

    @classmethod
    def set_parameters(cls, cat_key, parameters):
        cls._parameters_cache[cat_key] = parameters

    @classmethod
    def clear_all(cls):
        cls._categories_cache.clear()
        cls._elements_cache.clear()
        cls._parameters_cache.clear()
