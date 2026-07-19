# -*- coding: utf-8 -*-
"""Safe room-parameter reads and writes."""
from Autodesk.Revit.DB import StorageType, BuiltInParameter
from rdm.utils.units import UnitHelper
try:
    from rdm.config import DEVELOPER_DEBUG_MODE
except Exception:
    DEVELOPER_DEBUG_MODE = False


class ParameterService(object):
    def __init__(self, doc):
        self.doc = doc
        self.unit_helper = UnitHelper(doc)

    def read(self, room, parameter_name):
        params = room.GetParameters(parameter_name)
        if not params:
            return None
            
        # Diagnostic logger helper
        def log_read(found_name, storage, raw_val, parsed_val, ret_val):
            if DEVELOPER_DEBUG_MODE:
                try:
                    num = room.get_Parameter(BuiltInParameter.ROOM_NUMBER)
                    r_num = num.AsString() if num else "Unknown"
                    if r_num == "2":
                        print("=== PARAMETER SERVICE TRACE ===")
                        print("Requested Parameter Name: {}".format(parameter_name))
                        print("Found Parameter Name: {}".format(found_name))
                        print("StorageType: {}".format(storage))
                        print("Raw Internal Value: {}".format(raw_val))
                        print("Parsed Value: {}".format(parsed_val))
                        print("Returned Value: {}".format(ret_val))
                        print("===============================")
                except Exception:
                    pass

        # First pass: look for a valid Double parameter with a non-zero value
        for param in params:
            if not param.IsReadOnly and param.StorageType == StorageType.Double:
                if param.HasValue:
                    val = param.AsDouble()
                    if val != 0.0:
                        log_read(param.Definition.Name, "Double", val, "N/A", val)
                        return val

        # Second pass: look for any Double parameter
        for param in params:
            if not param.IsReadOnly and param.StorageType == StorageType.Double:
                val = param.AsDouble() if param.HasValue else 0.0
                log_read(param.Definition.Name, "Double", param.AsDouble() if param.HasValue else "No Value", "N/A", val)
                return val
                
        # Third pass: look for String parameter and parse using Revit Project Units
        for param in params:
            if not param.IsReadOnly and param.StorageType == StorageType.String:
                if param.HasValue:
                    raw_str = param.AsString()
                    parsed = self.unit_helper.parse_length(raw_str)
                    if parsed is not None:
                        log_read(param.Definition.Name, "String", raw_str, parsed, parsed)
                        return parsed
                        
        # Fallback: if no writable parameter found, read the first read-only one (as a last resort)
        for param in params:
            if param.IsReadOnly:
                if param.StorageType == StorageType.Double:
                    val = param.AsDouble() if param.HasValue else 0.0
                    log_read(param.Definition.Name, "Double (ReadOnly Fallback)", param.AsDouble() if param.HasValue else "No Value", "N/A", val)
                    return val
                elif param.StorageType == StorageType.String and param.HasValue:
                    raw_str = param.AsString()
                    parsed = self.unit_helper.parse_length(raw_str)
                    if parsed is not None:
                        log_read(param.Definition.Name, "String (ReadOnly Fallback)", raw_str, parsed, parsed)
                        return parsed
                        
        if DEVELOPER_DEBUG_MODE:
            try:
                num = room.get_Parameter(BuiltInParameter.ROOM_NUMBER)
                if num and num.AsString() == "2":
                    print("=== PARAMETER SERVICE TRACE ===")
                    print("Requested Parameter Name: {}".format(parameter_name))
                    print("Found Parameter Name: NONE")
                    print("Returned Value: None")
                    print("===============================")
            except Exception:
                pass
        return None

    def write(self, room, parameter_name, value):
        params = room.GetParameters(parameter_name)
        if not params:
            raise ValueError("Missing parameter: {0}".format(parameter_name))
            
        target_param = None
        for param in params:
            if not param.IsReadOnly:
                if param.StorageType == StorageType.Double:
                    target_param = param
                    break
                elif param.StorageType == StorageType.String and target_param is None:
                    target_param = param
                    
        if target_param is None:
            raise ValueError("Read-only parameter: {0}".format(parameter_name))
            
        if target_param.StorageType == StorageType.Double:
            target_param.Set(value)
        elif target_param.StorageType == StorageType.String:
            # If the user specifically chose a String parameter, write the project-unit formatted string
            val_str = self.unit_helper.format_length(value)
            target_param.Set(val_str)
