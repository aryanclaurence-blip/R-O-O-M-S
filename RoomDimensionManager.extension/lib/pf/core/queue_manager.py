# -*- coding: utf-8 -*-
"""Queue Manager for PARAMS FLOW Mapping Engine."""

class QueueStatistics(object):
    def __init__(self, total=0, enabled=0, disabled=0, categories=0, estimated_targets=0):
        self.total = total
        self.enabled = enabled
        self.disabled = disabled
        self.categories = categories
        self.estimated_targets = estimated_targets

class PFQueueManager(object):
    def __init__(self):
        self._mappings = []

    def get_all(self):
        return list(self._mappings)

    def add_mapping(self, mapping_obj):
        self._mappings.append(mapping_obj)
        return mapping_obj

    def remove_mapping(self, mapping_obj):
        if mapping_obj in self._mappings:
            self._mappings.remove(mapping_obj)

    def clear(self):
        self._mappings = []

    def duplicate_mapping(self, mapping_obj):
        cloned = mapping_obj.clone()
        idx = self._mappings.index(mapping_obj) if mapping_obj in self._mappings else len(self._mappings)
        self._mappings.insert(idx + 1, cloned)
        return cloned

    def move_up(self, mapping_obj):
        if mapping_obj in self._mappings:
            idx = self._mappings.index(mapping_obj)
            if idx > 0:
                self._mappings[idx], self._mappings[idx - 1] = self._mappings[idx - 1], self._mappings[idx]

    def move_down(self, mapping_obj):
        if mapping_obj in self._mappings:
            idx = self._mappings.index(mapping_obj)
            if idx < len(self._mappings) - 1:
                self._mappings[idx], self._mappings[idx + 1] = self._mappings[idx + 1], self._mappings[idx]

    def move_top(self, mapping_obj):
        if mapping_obj in self._mappings:
            self._mappings.remove(mapping_obj)
            self._mappings.insert(0, mapping_obj)

    def move_bottom(self, mapping_obj):
        if mapping_obj in self._mappings:
            self._mappings.remove(mapping_obj)
            self._mappings.append(mapping_obj)

    def is_duplicate(self, mapping_obj):
        for m in self._mappings:
            if m.id != mapping_obj.id:
                if (m.source_param == mapping_obj.source_param and
                    m.target_param == mapping_obj.target_param and
                    m.target_cat == mapping_obj.target_cat and
                    m.mapping_type == mapping_obj.mapping_type):
                    return True
        return False

    def get_statistics(self, default_target_count=0):
        total = len(self._mappings)
        enabled = sum(1 for m in self._mappings if getattr(m, 'enabled', True))
        disabled = total - enabled
        cats = len(set(getattr(m, 'target_cat', 'Rooms') for m in self._mappings))
        return QueueStatistics(total, enabled, disabled, cats, default_target_count * enabled)
