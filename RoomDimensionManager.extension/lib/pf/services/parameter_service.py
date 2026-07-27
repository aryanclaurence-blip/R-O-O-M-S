# -*- coding: utf-8 -*-
"""Parameter discovery, reading, conversion, and writing service for PARAMS FLOW."""
from Autodesk.Revit.DB import StorageType, ElementId

class PFParameterService(object):
    def __init__(self, doc):
        self.doc = doc

    def discover_parameters_for_elements(self, elements):
        """Returns sorted list of unique parameter names found across elements."""
        names = set()
        for elem in elements[:50]:  # Inspect first 50 elements for speed
            try:
                for p in elem.Parameters:
                    try:
                        if p.Definition and p.Definition.Name:
                            names.add(p.Definition.Name)
                    except Exception:
                        pass
            except Exception:
                pass
        return sorted(names)

    def read_param_as_string(self, element, param_name):
        """Read any parameter on element and return string representation."""
        if not element or not param_name:
            return ""
        params = element.GetParameters(param_name)
        if not params:
            return ""
        for p in params:
            if not p.HasValue:
                continue
            if p.StorageType == StorageType.String:
                return p.AsString() or ""
            elif p.StorageType == StorageType.Double:
                return str(p.AsDouble())
            elif p.StorageType == StorageType.Integer:
                return str(p.AsInteger())
            elif p.StorageType == StorageType.ElementId:
                eid = p.AsElementId()
                return str(eid.IntegerValue) if hasattr(eid, 'IntegerValue') else str(eid)
            else:
                return p.AsValueString() or ""
        return ""

    def write_param_value(self, element, param_name, new_val_str):
        """Safely write new_val_str to param_name on element with StorageType conversion."""
        if not element or not param_name:
            return False, "Invalid element or parameter name"
        params = element.GetParameters(param_name)
        if not params:
            return False, "Parameter '{}' missing on element".format(param_name)

        target_param = None
        for p in params:
            if not p.IsReadOnly:
                target_param = p
                break
        if not target_param:
            return False, "Parameter '{}' is READ ONLY".format(param_name)

        try:
            st = target_param.StorageType
            if st == StorageType.String:
                target_param.Set(str(new_val_str))
                return True, "OK"
            elif st == StorageType.Double:
                val = float(new_val_str)
                target_param.Set(val)
                return True, "OK"
            elif st == StorageType.Integer:
                val = int(float(new_val_str))
                target_param.Set(val)
                return True, "OK"
            elif st == StorageType.ElementId:
                eid_val = int(new_val_str)
                target_param.Set(ElementId(eid_val))
                return True, "OK"
            else:
                target_param.Set(str(new_val_str))
                return True, "OK"
        except Exception as e:
            return False, str(e)
