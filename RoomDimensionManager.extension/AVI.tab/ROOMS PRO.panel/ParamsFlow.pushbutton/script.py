# -*- coding: utf-8 -*-
"""PARAMS FLOW - Enterprise Parameter Flow & Mapping Tool."""
import os
import sys

LIB_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'lib'))
if LIB_DIR not in sys.path:
    sys.path.insert(0, LIB_DIR)

from pf.ui.params_flow_window import ParamsFlowWindow

ParamsFlowWindow().ShowDialog()
