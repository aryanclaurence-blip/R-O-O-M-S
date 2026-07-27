# -*- coding: utf-8 -*-
"""Validation Engine for PARAMS FLOW."""
from pf.core.mapping import MappingType

class ValidationResult(object):
    def __init__(self, mapping, status="VALID", message="OK", valid_count=0, readonly_count=0, missing_count=0):
        self.mapping = mapping
        self.status = status
        self.message = message
        self.valid_count = valid_count
        self.readonly_count = readonly_count
        self.missing_count = missing_count

class ValidationEngine(object):
    def __init__(self, doc):
        self.doc = doc

    def validate_mapping(self, mapping, elements):
        """Validate a single mapping against target elements."""
        if not mapping.target_param:
            return ValidationResult(mapping, "ERROR", "Target Parameter is required", 0, 0, 0)

        if mapping.mapping_type == MappingType.COPY and not mapping.source_param:
            return ValidationResult(mapping, "ERROR", "Source Parameter is required for Copy mode", 0, 0, 0)

        valid = 0
        readonly = 0
        missing = 0

        for elem in elements:
            params = elem.GetParameters(mapping.target_param)
            if not params:
                missing += 1
                continue
            
            is_ro = True
            for p in params:
                if not p.IsReadOnly:
                    is_ro = False
                    break
            if is_ro:
                readonly += 1
            else:
                valid += 1

        if missing == len(elements) and len(elements) > 0:
            return ValidationResult(mapping, "MISSING PARAMETER", "Target parameter missing on all elements", valid, readonly, missing)
        elif readonly == len(elements) and len(elements) > 0:
            return ValidationResult(mapping, "READ ONLY", "Target parameter is read-only on all elements", valid, readonly, missing)
        elif missing > 0 or readonly > 0:
            return ValidationResult(mapping, "WARNING", "Partial compatibility: {} valid, {} read-only, {} missing".format(valid, readonly, missing), valid, readonly, missing)
        else:
            return ValidationResult(mapping, "VALID", "Target parameter is valid on all {} elements".format(valid), valid, readonly, missing)
