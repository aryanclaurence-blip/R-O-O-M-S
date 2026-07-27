# -*- coding: utf-8 -*-
"""Batch Execution Engine for PARAMS FLOW."""
from Autodesk.Revit.DB import Transaction
from pf.core.mapping import MappingType
from pf.core.sequence import SequenceGenerator
from pf.services.parameter_service import PFParameterService
from pf.models.element_row import ElementResultRow

class BatchExecutor(object):
    def __init__(self, doc):
        self.doc = doc
        self.param_service = PFParameterService(doc)

    def execute_mappings(self, mappings, elements, session=None):
        """Execute mappings queue across elements within a safe Revit Transaction."""
        results = []
        if not elements or not mappings:
            return results

        t = Transaction(self.doc, "PARAMS FLOW Batch Apply")
        t.Start()
        
        success_count = 0
        fail_count = 0

        for elem_idx, elem in enumerate(elements):
            elem_id_val = elem.Id.IntegerValue if hasattr(elem.Id, 'IntegerValue') else elem.Id
            cat_name = elem.Category.Name if elem.Category else "Unknown"

            for m in mappings:
                if not m.target_param:
                    continue

                source_mapping_name = m.source_param if m.mapping_type == MappingType.COPY else m.mapping_type
                old_val = self.param_service.read_param_as_string(elem, m.target_param)
                new_val = ""

                # Generate new proposed value
                try:
                    if m.mapping_type == MappingType.COPY:
                        new_val = self.param_service.read_param_as_string(elem, m.source_param)
                    elif m.mapping_type == MappingType.STATIC:
                        new_val = m.static_value
                    elif m.mapping_type == MappingType.SEQUENCE:
                        seq_gen = SequenceGenerator(m.seq_pattern, m.seq_start, m.seq_step)
                        new_val = seq_gen.generate_value(elem_idx)
                    elif m.mapping_type == MappingType.FIND_REPLACE:
                        src_raw = self.param_service.read_param_as_string(elem, m.source_param)
                        new_val = src_raw.replace(m.find_str, m.replace_str) if m.find_str else src_raw
                except Exception as ex:
                    res_row = ElementResultRow(elem, cat_name, source_mapping_name, m.target_param, old_val, "", "FAILED", str(ex))
                    results.append(res_row)
                    fail_count += 1
                    continue

                # Write to target parameter safely
                try:
                    ok, msg = self.param_service.write_param_value(elem, m.target_param, new_val)
                    if ok:
                        res_row = ElementResultRow(elem, cat_name, source_mapping_name, m.target_param, old_val, new_val, "UPDATED", "OK")
                        results.append(res_row)
                        success_count += 1
                    else:
                        status_code = "READ ONLY" if "READ ONLY" in msg else ("MISSING PARAMETER" if "missing" in msg else "FAILED")
                        res_row = ElementResultRow(elem, cat_name, source_mapping_name, m.target_param, old_val, new_val, status_code, msg)
                        results.append(res_row)
                        fail_count += 1
                except Exception as ex:
                    res_row = ElementResultRow(elem, cat_name, source_mapping_name, m.target_param, old_val, new_val, "FAILED", str(ex))
                    results.append(res_row)
                    fail_count += 1

        t.Commit()

        if session:
            session.log_info("Batch Execution Complete. Updated: {}, Failed/Skipped: {}".format(success_count, fail_count))

        return results
