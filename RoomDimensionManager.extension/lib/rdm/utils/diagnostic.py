# -*- coding: utf-8 -*-
import os

def log_parameter_info(room, parameter_name, filepath):
    with open(filepath, 'a') as f:
        f.write("=== DIAGNOSTIC LOG FOR ROOM {} ===\n".format(room.Id.IntegerValue))
        f.write("Target Parameter: {}\n".format(parameter_name))
        
        params = room.GetParameters(parameter_name)
        if not params:
            f.write("ERROR: No parameters found with name '{}'\n".format(parameter_name))
            return
            
        for p in params:
            f.write("\n--- Parameter Instance ---\n")
            f.write("Name: {}\n".format(p.Definition.Name))
            try:
                f.write("IsShared: {}\n".format(p.IsShared))
                if p.IsShared:
                    f.write("GUID: {}\n".format(p.GUID))
            except Exception:
                pass
            
            f.write("StorageType: {}\n".format(p.StorageType))
            f.write("HasValue: {}\n".format(p.HasValue))
            f.write("IsReadOnly: {}\n".format(p.IsReadOnly))
            
            try:
                f.write("AsDouble(): {}\n".format(p.AsDouble()))
            except Exception as e:
                f.write("AsDouble(): Error - {}\n".format(e))
                
            try:
                f.write("AsString(): {}\n".format(p.AsString()))
            except Exception as e:
                f.write("AsString(): Error - {}\n".format(e))
                
            try:
                f.write("AsValueString(): {}\n".format(p.AsValueString()))
            except Exception as e:
                f.write("AsValueString(): Error - {}\n".format(e))
        f.write("\n")
