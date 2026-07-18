# -*- coding: utf-8 -*-
"""IronPython-compatible polygon representations."""


class Point2D(object):
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)


class PolygonModel(object):
    def __init__(self, vertices=None):
        self.vertices = vertices or []
