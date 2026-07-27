try:
    from Autodesk.Revit.DB import StorageType
except ImportError:
    class StorageType(object):
        String = "String"
        Double = "Double"
        Integer = "Integer"
        ElementId = "ElementId"
from pf.core.mapping import MappingType

class ValidationSummary(object):
    def __init__(self, total_mappings=0, ready=0, warnings=0, errors=0, affected_elements=0, preview_rows=0):
        self.total_mappings = total_mappings
        self.ready = ready
        self.warnings = warnings
        self.errors = errors
        self.affected_elements = affected_elements
        self.preview_rows = preview_rows

class ValidationReport(object):
    def __init__(self, mapping, status="Ready", message="OK", valid_targets=0, readonly_targets=0, missing_targets=0, type_warning=""):
        self.mapping = mapping
        self.status = status
        self.message = message
        self.valid_targets = valid_targets
        self.readonly_targets = readonly_targets
        self.missing_targets = missing_targets
        self.type_warning = type_warning

class PFValidationEngine(object):
    def __init__(self, doc):
        self.doc = doc

    def validate_mapping(self, mapping, elements):
        """Validate a single mapping rule against target elements."""
        if not getattr(mapping, 'enabled', True):
            return ValidationReport(mapping, "Disabled", "Mapping is disabled", 0, 0, 0)

        if not mapping.target_param:
            return ValidationReport(mapping, "Error", "Target Parameter is required", 0, 0, 0)

        if mapping.mapping_type == MappingType.COPY and not mapping.source_param:
            return ValidationReport(mapping, "Error", "Source Parameter is required for Parameter Copy mode", 0, 0, 0)

        if not elements:
            return ValidationReport(mapping, "Warning", "No target elements found in selected scope", 0, 0, 0)

        valid_count = 0
        readonly_count = 0
        missing_count = 0

        for elem in elements:
            params = elem.GetParameters(mapping.target_param)
            if not params:
                missing_count += 1
                continue

            is_ro = True
            for p in params:
                if not p.IsReadOnly:
                    is_ro = False
                    break
            if is_ro:
                readonly_count += 1
            else:
                valid_count += 1

        total_elems = len(elements)
        if missing_count == total_elems:
            return ValidationReport(mapping, "Error", "Target Parameter '{}' missing on all {} elements".format(mapping.target_param, total_elems), valid_count, readonly_count, missing_count)
        elif readonly_count == total_elems:
            return ValidationReport(mapping, "Error", "Target Parameter '{}' is READ ONLY on all {} elements".format(mapping.target_param, total_elems), valid_count, readonly_count, missing_count)
        elif missing_count > 0 or readonly_count > 0:
            return ValidationReport(mapping, "Warning", "Partial Compatibility: {} valid, {} read-only, {} missing".format(valid_count, readonly_count, missing_count), valid_count, readonly_count, missing_count)
        else:
            return ValidationReport(mapping, "Ready", "Valid on all {} elements".format(valid_count), valid_count, readonly_count, missing_count)

    def validate_queue(self, mappings, element_provider):
        """Validate full mapping queue across scope elements."""
        reports = []
        summary = ValidationSummary(total_mappings=len(mappings))
        all_affected = set()

        for m in mappings:
            if not getattr(m, 'enabled', True):
                reports.append(ValidationReport(m, "Disabled", "Mapping is disabled"))
                continue

            elems = element_provider(m.source_scope, m.target_cat)
            report = self.validate_mapping(m, elems)
            reports.append(report)

            if report.status == "Ready":
                summary.ready += 1
            elif report.status == "Warning":
                summary.warnings += 1
            elif report.status == "Error":
                summary.errors += 1

            for e in elems:
                all_affected.add(e.Id)

        summary.affected_elements = len(all_affected)
        return reports, summary
