# -*- coding: utf-8 -*-
"""
Models for the Graphics Override Engine.
IronPython 2.7 compatible.
"""
from rdm.models.value_objects import Color

class GraphicsConfiguration(object):
    """Settings governing how overrides are constructed and applied."""
    def __init__(self, color_pass=None, color_fail=None, color_review=None, color_warning=None, color_not_calculated=None, color_read_only=None, color_missing=None, color_unsupported=None, solid_fill_pattern_name="<Solid fill>"):
        self.color_pass = color_pass or Color(0, 255, 0)
        self.color_fail = color_fail or Color(255, 0, 0)
        self.color_review = color_review or Color(255, 255, 0)
        self.color_warning = color_warning or Color(255, 165, 0)
        self.color_not_calculated = color_not_calculated or Color(128, 128, 128)
        self.color_read_only = color_read_only or Color(0, 0, 255)
        self.color_missing = color_missing or Color(128, 0, 128)
        self.color_unsupported = color_unsupported or Color(64, 64, 64)
        self.solid_fill_pattern_name = solid_fill_pattern_name

class OverrideStyle(object):
    """An immutable definition of a visual override state."""
    def __init__(self, override_type, projection_fill_color=None, projection_line_color=None, surface_transparency=0, halftone=False):
        self.override_type = override_type
        self.projection_fill_color = projection_fill_color
        self.projection_line_color = projection_line_color
        self.surface_transparency = surface_transparency
        self.halftone = halftone

class ViewOverride(object):
    """An association of a specific element to a specific override within a view."""
    def __init__(self, view_id, element_id, style):
        self.view_id = view_id
        self.element_id = element_id
        self.style = style
