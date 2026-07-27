# -*- coding: utf-8 -*-
"""Mapping Integrity & Migration Engine for PARAMS FLOW."""
import time

class MappingHealth(object):
    HEALTHY = "HEALTHY"
    COMPATIBLE = "COMPATIBLE"
    NEEDS_MIGRATION = "NEEDS_MIGRATION"
    NEEDS_REPAIR = "NEEDS_REPAIR"
    BROKEN = "BROKEN"

class IntegrityReport(object):
    def __init__(self, mapping, health=MappingHealth.HEALTHY, message="Ok", suggested_param=None):
        self.mapping = mapping
        self.health = health
        self.message = message
        self.suggested_param = suggested_param

class IntegritySummary(object):
    def __init__(self):
        self.total_loaded = 0
        self.healthy_count = 0
        self.compatible_count = 0
        self.needs_migration_count = 0
        self.needs_repair_count = 0
        self.broken_count = 0
        self.auto_repaired_count = 0

class PFIntegrityEngine(object):
    def __init__(self, doc=None):
        self.doc = doc

    def scan_mapping(self, mapping, available_source_params=None, available_target_params=None):
        """Scan a mapping item for integrity, version drift, and parameter renaming."""
        available_source_params = available_source_params or []
        available_target_params = available_target_params or []

        # Validate Target Parameter
        tgt_param = getattr(mapping, 'target_param', '')
        if not tgt_param:
            return IntegrityReport(mapping, MappingHealth.BROKEN, "Target Parameter is missing.")

        if available_target_params and tgt_param not in available_target_params:
            # Case-insensitive fuzzy match attempt
            fuzzy_match = None
            for p in available_target_params:
                if p.lower() == tgt_param.lower():
                    fuzzy_match = p
                    break
            if fuzzy_match:
                return IntegrityReport(
                    mapping, MappingHealth.NEEDS_MIGRATION,
                    "Target Parameter '{}' renamed to '{}'.".format(tgt_param, fuzzy_match),
                    suggested_param=fuzzy_match
                )
            return IntegrityReport(mapping, MappingHealth.NEEDS_REPAIR, "Target Parameter '{}' not found in category.".format(tgt_param))

        # Validate Source Parameter if required by mapping mode
        mode = getattr(mapping, 'mapping_type', '')
        src_param = getattr(mapping, 'source_param', '')
        if mode in ["Parameter Copy", "Find & Replace", "Prefix", "Suffix", "Upper Case", "Lower Case", "Title Case", "Trim"]:
            if not src_param:
                return IntegrityReport(mapping, MappingHealth.BROKEN, "Source Parameter is required.")
            if available_source_params and src_param not in available_source_params:
                fuzzy_src = None
                for p in available_source_params:
                    if p.lower() == src_param.lower():
                        fuzzy_src = p
                        break
                if fuzzy_src:
                    return IntegrityReport(
                        mapping, MappingHealth.NEEDS_MIGRATION,
                        "Source Parameter '{}' renamed to '{}'.".format(src_param, fuzzy_src),
                        suggested_param=fuzzy_src
                    )
                return IntegrityReport(mapping, MappingHealth.NEEDS_REPAIR, "Source Parameter '{}' not found in source category.".format(src_param))

        return IntegrityReport(mapping, MappingHealth.HEALTHY, "Mapping integrity verified.")

    def scan_queue(self, mappings, source_params=None, target_params=None):
        """Perform a complete queue integrity scan."""
        reports = []
        summary = IntegritySummary()
        summary.total_loaded = len(mappings)

        for m in mappings:
            rep = self.scan_mapping(m, source_params, target_params)
            reports.append(rep)
            if rep.health == MappingHealth.HEALTHY:
                summary.healthy_count += 1
            elif rep.health == MappingHealth.COMPATIBLE:
                summary.compatible_count += 1
            elif rep.health == MappingHealth.NEEDS_MIGRATION:
                summary.needs_migration_count += 1
            elif rep.health == MappingHealth.NEEDS_REPAIR:
                summary.needs_repair_count += 1
            else:
                summary.broken_count += 1

        return reports, summary

    def auto_repair_queue(self, mappings, reports):
        """Perform automatic migration repairs for fuzzy parameter matches."""
        repaired_count = 0
        for rep in reports:
            if rep.health == MappingHealth.NEEDS_MIGRATION and rep.suggested_param:
                rep.mapping.target_param = rep.suggested_param
                rep.mapping.status = "Auto-Repaired"
                rep.health = MappingHealth.HEALTHY
                repaired_count += 1
        return repaired_count
