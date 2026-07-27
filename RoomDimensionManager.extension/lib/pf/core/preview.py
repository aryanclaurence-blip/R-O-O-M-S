# -*- coding: utf-8 -*-
"""Preview Generator Engine for PARAMS FLOW."""
from pf.core.mapping import MappingType
from pf.core.sequence import SequenceGenerator
from pf.services.parameter_service import PFParameterService
from pf.models.element_row import ElementResultRow

class PFPreviewEngine(object):
    def __init__(self, doc):
        self.doc = doc
        self.param_service = PFParameterService(doc)

    def generate_preview(self, mappings, element_provider, limit=100):
        """Simulates mapping logic and returns preview rows up to limit."""
        preview_rows = []
        if not mappings:
            return preview_rows

        row_count = 0
        for m in mappings:
            if not getattr(m, 'enabled', True) or not m.target_param:
                continue

            elems = element_provider(m.source_scope, m.target_cat)
            source_display_name = m.source_param if m.mapping_type in [MappingType.COPY, MappingType.FIND_REPLACE, MappingType.PREFIX, MappingType.SUFFIX] else m.mapping_type

            for idx, elem in enumerate(elems):
                if row_count >= limit:
                    break

                old_val = self.param_service.read_param_as_string(elem, m.target_param)
                proposed_val = ""

                try:
                    if m.mapping_type == MappingType.COPY:
                        proposed_val = self.param_service.read_param_as_string(elem, m.source_param)
                    elif m.mapping_type == MappingType.STATIC:
                        proposed_val = m.static_value
                    elif m.mapping_type == MappingType.SEQUENCE:
                        seq_gen = SequenceGenerator(m.seq_pattern, m.seq_start, m.seq_step)
                        proposed_val = seq_gen.generate(idx)
                    elif m.mapping_type == MappingType.FIND_REPLACE:
                        raw = self.param_service.read_param_as_string(elem, m.source_param)
                        proposed_val = raw.replace(m.find_str, m.replace_str) if m.find_str else raw
                    elif m.mapping_type == MappingType.PREFIX:
                        raw = self.param_service.read_param_as_string(elem, m.source_param)
                        proposed_val = "{}{}".format(m.prefix_str, raw)
                    elif m.mapping_type == MappingType.SUFFIX:
                        raw = self.param_service.read_param_as_string(elem, m.source_param)
                        proposed_val = "{}{}".format(raw, m.suffix_str)
                    elif m.mapping_type == MappingType.UPPER_CASE:
                        raw = self.param_service.read_param_as_string(elem, m.source_param)
                        proposed_val = raw.upper()
                    elif m.mapping_type == MappingType.LOWER_CASE:
                        raw = self.param_service.read_param_as_string(elem, m.source_param)
                        proposed_val = raw.lower()
                    elif m.mapping_type == MappingType.TITLE_CASE:
                        raw = self.param_service.read_param_as_string(elem, m.source_param)
                        proposed_val = raw.title()
                    elif m.mapping_type == MappingType.TRIM:
                        raw = self.param_service.read_param_as_string(elem, m.source_param)
                        proposed_val = raw.strip()
                    elif m.mapping_type == MappingType.TRIM_START:
                        raw = self.param_service.read_param_as_string(elem, m.source_param)
                        proposed_val = raw.lstrip()
                    elif m.mapping_type == MappingType.TRIM_END:
                        raw = self.param_service.read_param_as_string(elem, m.source_param)
                        proposed_val = raw.rstrip()
                    elif m.mapping_type == MappingType.CLEAR_VALUE:
                        proposed_val = ""
                except Exception as ex:
                    proposed_val = "[ERR: {}]".format(ex)

                row = ElementResultRow(elem, m.target_cat, source_display_name, m.target_param, old_val, proposed_val, "PREVIEW", "Simulation Only")
                preview_rows.append(row)
                row_count += 1

            if row_count >= limit:
                break

        return preview_rows
