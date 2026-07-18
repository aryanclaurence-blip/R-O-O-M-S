# -*- coding: utf-8 -*-
"""Room domain model used by services and workflows."""


class RoomModel(object):
    def __init__(self, id, name, number, status, revit_element=None):
        self.id = id
        self.name = name
        self.number = number
        self.status = status
        self.revit_element = revit_element
