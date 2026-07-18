# -*- coding: utf-8 -*-
"""
Application domain models.
IronPython 2.7 compatible.
"""

class AppVersion(object):
    def __init__(self, major, minor, patch):
        self.major = major
        self.minor = minor
        self.patch = patch
        
    def __str__(self):
        return "{0}.{1}.{2}".format(self.major, self.minor, self.patch)

class PluginContext(object):
    def __init__(self, version=None, revit_version="Unknown", is_debug=False):
        self.version = version or AppVersion(1, 0, 0)
        self.revit_version = revit_version
        self.is_debug = is_debug

class CommandContext(object):
    def __init__(self, command_name, active_document_id=None, active_view_id=None):
        self.command_name = command_name
        self.active_document_id = active_document_id
        self.active_view_id = active_view_id

class CommandResult(object):
    def __init__(self, success, message=""):
        self.success = success
        self.message = message
