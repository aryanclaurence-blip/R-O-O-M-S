# -*- coding: utf-8 -*-
"""
Room Dimension Manager - Enterprise
Entry point script for the pyRevit extension.
"""
__title__ = "Room Dimension\nManager"
__author__ = "Enterprise Arch"

import sys
import os

# Append the lib directory to the sys.path so we can import our framework
lib_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'lib'))
if lib_dir not in sys.path:
    sys.path.insert(0, lib_dir)

try:
    # pyRevit executes this script directly.  There is deliberately no
    # IExternalCommand, availability class, DLL, or external-tools bridge.
    from rdm.ui.application import RoomDimensionManagerWindow
    RoomDimensionManagerWindow().ShowDialog()
except Exception as e:
    import traceback
    traceback.print_exc()
    from pyrevit import forms
    forms.alert("Failed to initialize Room Dimension Manager:\\n{0}".format(str(e)), title="Fatal Error")
