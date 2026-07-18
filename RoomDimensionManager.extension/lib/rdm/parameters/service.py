# -*- coding: utf-8 -*-
"""Safe room-parameter reads and writes."""
from Autodesk.Revit.DB import StorageType


class ParameterService(object):
    def read(self, room, parameter_name):
        parameter = room.LookupParameter(parameter_name)
        if parameter and parameter.HasValue and parameter.StorageType == StorageType.Double:
            return parameter.AsDouble()
        return None

    def write(self, room, parameter_name, value):
        parameter = room.LookupParameter(parameter_name)
        if parameter is None:
            raise ValueError("Missing parameter: {0}".format(parameter_name))
        if parameter.IsReadOnly:
            raise ValueError("Read-only parameter: {0}".format(parameter_name))
        if parameter.StorageType != StorageType.Double:
            raise ValueError("Parameter must be a Length/Double: {0}".format(parameter_name))
        parameter.Set(value)
