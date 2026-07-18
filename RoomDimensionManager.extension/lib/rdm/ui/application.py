# -*- coding: utf-8 -*-
"""Pure pyRevit WPF host for the Room Dimension Manager."""
import os

from pyrevit import forms, revit

from rdm.configuration.models import AppConfiguration
from rdm.ui.viewmodels.main_vm import MainViewModel


class RoomDimensionManagerWindow(forms.WPFWindow):
    """The sole UI host.  It is opened directly by the pushbutton script."""

    def __init__(self):
        xaml_path = os.path.join(os.path.dirname(__file__), "views", "MainWindow.xaml")
        forms.WPFWindow.__init__(self, xaml_path)

        self._config = AppConfiguration()
        self.DataContext = MainViewModel(self._config)
        self._set_document_context()

    def _set_document_context(self):
        """Populate harmless display-only context without an external command."""
        vm = self.DataContext
        doc = revit.doc
        if doc:
            vm.ProjectName = doc.Title
            vm.ModelName = doc.PathName or "Unsaved model"
            vm.RevitVersion = doc.Application.VersionName
