# -*- coding: utf-8 -*-
"""Execution Engine for PARAMS FLOW."""
import time
from pf.core.mapping import MappingType
from pf.core.sequence import SequenceGenerator
from pf.core.transaction_engine import PFTransactionEngine
from pf.services.parameter_service import PFParameterService
from pf.models.element_row import ElementResultRow

try:
    from Autodesk.Revit.DB import Transaction
except ImportError:
    class Transaction(object):
        def __init__(self, doc, name): pass
        def Start(self): pass
        def Commit(self): pass
        def RollBack(self): pass

class ExecutionSummary(object):
    def __init__(self, mappings_count=0, processed_count=0, updated_count=0, skipped_count=0, failed_count=0, elapsed_time=0.0):
        self.mappings_count = mappings_count
        self.processed_count = processed_count
        self.updated_count = updated_count
        self.skipped_count = skipped_count
        self.failed_count = failed_count
        self.elapsed_time = elapsed_time

    @property
    def success_rate(self):
        if self.processed_count == 0: return 100.0
        return (float(self.updated_count) / float(self.processed_count)) * 100.0

class PFExecutionEngine(object):
    def __init__(self, doc):
        self.doc = doc
        self.param_service = PFParameterService(doc)
        self.trans_engine = PFTransactionEngine(doc)

    def execute(self, mappings, element_provider, progress_callback=None, cancel_checker=None):
        """Executes mapping queue within TransactionGroup & safe Transactions."""
        t_start = time.time()
        results = []
        summary = ExecutionSummary(mappings_count=len(mappings))

        def run_batch():
            for m_idx, m in enumerate(mappings, start=1):
                if not getattr(m, 'enabled', True) or not m.target_param:
                    continue

                if cancel_checker and cancel_checker():
                    break

                elems = element_provider(m.source_scope, m.target_cat)
                source_display_name = m.source_param if m.mapping_type in [MappingType.COPY, MappingType.FIND_REPLACE, MappingType.PREFIX, MappingType.SUFFIX] else m.mapping_type

                t = Transaction(self.doc, "PARAMS FLOW: {}".format(m.target_param))
                t.Start()

                for e_idx, elem in enumerate(elems):
                    if cancel_checker and cancel_checker():
                        break

                    summary.processed_count += 1
                    if progress_callback:
                        progress_callback(m_idx, len(mappings), e_idx + 1, len(elems))

                    if not elem or not hasattr(elem, 'Id'):
                        results.append(ElementResultRow(elem, m.target_cat, source_display_name, m.target_param, "-", "-", "Element Missing", "Element null or deleted"))
                        summary.failed_count += 1
                        continue

                    if getattr(elem, "IsPinned", False):
                        results.append(ElementResultRow(elem, m.target_cat, source_display_name, m.target_param, "-", "-", "Skipped", "Element is Pinned"))
                        summary.skipped_count += 1
                        continue

                    old_val = self.param_service.read_param_as_string(elem, m.target_param)
                    proposed_val = ""

                    try:
                        if m.mapping_type == MappingType.COPY:
                            proposed_val = self.param_service.read_param_as_string(elem, m.source_param)
                        elif m.mapping_type == MappingType.STATIC:
                            proposed_val = m.static_value
                        elif m.mapping_type == MappingType.SEQUENCE:
                            seq_gen = SequenceGenerator(m.seq_pattern, m.seq_start, m.seq_step)
                            proposed_val = seq_gen.generate(e_idx)
                        elif m.mapping_type == MappingType.FIND_REPLACE:
                            raw = self.param_service.read_param_as_string(elem, m.source_param)
                            proposed_val = raw.replace(m.find_str, m.replace_str) if m.find_str else raw
                        elif m.mapping_type == MappingType.PREFIX:
                            raw = self.param_service.read_param_as_string(elem, m.source_param)
                            proposed_val = "{}{}".format(m.prefix_str, raw)
                        elif m.mapping_type == MappingType.SUFFIX:
                            raw = self.param_service.read_param_as_string(elem, m.source_param)
                            proposed_val = "{}{}".format(raw, m.suffix_str)
                    except Exception as ex:
                        results.append(ElementResultRow(elem, m.target_cat, source_display_name, m.target_param, old_val, "", "Failed", str(ex)))
                        summary.failed_count += 1
                        continue

                    try:
                        ok, msg = self.param_service.write_param_value(elem, m.target_param, proposed_val)
                        if ok:
                            results.append(ElementResultRow(elem, m.target_cat, source_display_name, m.target_param, old_val, proposed_val, "UPDATED", "OK"))
                            summary.updated_count += 1
                        else:
                            status_code = "READ ONLY" if "READ ONLY" in msg else ("Parameter Missing" if "missing" in msg else "Failed")
                            results.append(ElementResultRow(elem, m.target_cat, source_display_name, m.target_param, old_val, proposed_val, status_code, msg))
                            if status_code in ["READ ONLY", "Parameter Missing"]:
                                summary.skipped_count += 1
                            else:
                                summary.failed_count += 1
                    except Exception as ex:
                        results.append(ElementResultRow(elem, m.target_cat, source_display_name, m.target_param, old_val, proposed_val, "Failed", str(ex)))
                        summary.failed_count += 1

                t.Commit()

        self.trans_engine.execute_in_group("PARAMS FLOW Batch Apply", run_batch)
        summary.elapsed_time = time.time() - t_start
        return results, summary
