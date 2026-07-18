# -*- coding: utf-8 -*-
"""
MainViewModel for the Room Dimension Manager.
IronPython 2.7 compatible.
Controls the 5-Step UI workflow.
"""
from rdm.ui.viewmodels.base import ObservableObject, RelayCommand
import logging

logger = logging.getLogger(__name__)

class MainViewModel(ObservableObject):
    def __init__(self, config):
        super(MainViewModel, self).__init__()
        self.config = config
        
        # Header Info
        self._project_name = "Unknown Project"
        self._model_name = "Unknown Model"
        self._revit_version = "Unknown Version"
        
        # Step 1 & 2: Parameters
        self._available_parameters = ["Length", "Width", "Calculated Length", "Calculated Width"]
        self._selected_length_parameter = self.config.parameters.length_param_name
        self._selected_width_parameter = self.config.parameters.width_param_name
        
        # Step 3: Scope
        self._scope_entire_project = True
        self._scope_current_view = False
        self._scope_selected_rooms = False
        
        # Step 4: Tolerance
        self._tolerance = str(self.config.geometry.tolerance)
        self._document_unit_name = "ft"
        
        # Step 5: Operation
        self._operation_set_dimensions = False
        self._operation_cross_check = True
        
        # Status / Progress
        self._status_message = "Ready."
        self._is_processing = False
        self._progress_message = ""
        self._total_progress_items = 100
        self._current_progress_value = 0
        
        # Commands
        self.RunCommand = RelayCommand(self.run)
        self.CancelCommand = RelayCommand(self.cancel)
        self.ExportCsvCommand = RelayCommand(self.export_csv)
        self.ExportExcelCommand = RelayCommand(self.export_excel)
        self.ExportJsonCommand = RelayCommand(self.export_json)
        self.CopySummaryCommand = RelayCommand(self.copy_summary)
        self.OpenFolderCommand = RelayCommand(self.open_folder)
        self.SettingsCommand = RelayCommand(self.settings)
        self.HelpCommand = RelayCommand(self.help)
        
        # Results
        self._results_list = []

    # --- Properties ---
    
    @property
    def ProjectName(self): return self._project_name
    @ProjectName.setter
    def ProjectName(self, value):
        self._project_name = value
        self.on_property_changed("ProjectName")

    @property
    def ModelName(self): return self._model_name
    @ModelName.setter
    def ModelName(self, value):
        self._model_name = value
        self.on_property_changed("ModelName")
        
    @property
    def RevitVersion(self): return self._revit_version
    @RevitVersion.setter
    def RevitVersion(self, value):
        self._revit_version = value
        self.on_property_changed("RevitVersion")

    @property
    def AvailableParameters(self): return self._available_parameters
    
    @property
    def SelectedLengthParameter(self): return self._selected_length_parameter
    @SelectedLengthParameter.setter
    def SelectedLengthParameter(self, value):
        self._selected_length_parameter = value
        self.on_property_changed("SelectedLengthParameter")
        
    @property
    def SelectedWidthParameter(self): return self._selected_width_parameter
    @SelectedWidthParameter.setter
    def SelectedWidthParameter(self, value):
        self._selected_width_parameter = value
        self.on_property_changed("SelectedWidthParameter")

    @property
    def ScopeEntireProject(self): return self._scope_entire_project
    @ScopeEntireProject.setter
    def ScopeEntireProject(self, value):
        self._scope_entire_project = value
        self.on_property_changed("ScopeEntireProject")

    @property
    def ScopeCurrentView(self): return self._scope_current_view
    @ScopeCurrentView.setter
    def ScopeCurrentView(self, value):
        self._scope_current_view = value
        self.on_property_changed("ScopeCurrentView")

    @property
    def ScopeSelectedRooms(self): return self._scope_selected_rooms
    @ScopeSelectedRooms.setter
    def ScopeSelectedRooms(self, value):
        self._scope_selected_rooms = value
        self.on_property_changed("ScopeSelectedRooms")

    @property
    def Tolerance(self): return self._tolerance
    @Tolerance.setter
    def Tolerance(self, value):
        self._tolerance = value
        self.on_property_changed("Tolerance")

    @property
    def DocumentUnitName(self): return self._document_unit_name

    @property
    def OperationSetDimensions(self): return self._operation_set_dimensions
    @OperationSetDimensions.setter
    def OperationSetDimensions(self, value):
        self._operation_set_dimensions = value
        self.on_property_changed("OperationSetDimensions")

    @property
    def OperationCrossCheck(self): return self._operation_cross_check
    @OperationCrossCheck.setter
    def OperationCrossCheck(self, value):
        self._operation_cross_check = value
        self.on_property_changed("OperationCrossCheck")

    @property
    def StatusMessage(self): return self._status_message
    @StatusMessage.setter
    def StatusMessage(self, value):
        self._status_message = value
        self.on_property_changed("StatusMessage")
        
    @property
    def IsProcessing(self): return self._is_processing
    @IsProcessing.setter
    def IsProcessing(self, value):
        self._is_processing = value
        self.on_property_changed("IsProcessing")

    @property
    def ProgressMessage(self): return self._progress_message
    @ProgressMessage.setter
    def ProgressMessage(self, value):
        self._progress_message = value
        self.on_property_changed("ProgressMessage")
        
    @property
    def TotalProgressItems(self): return self._total_progress_items
    @TotalProgressItems.setter
    def TotalProgressItems(self, value):
        self._total_progress_items = value
        self.on_property_changed("TotalProgressItems")

    @property
    def CurrentProgressValue(self): return self._current_progress_value
    @CurrentProgressValue.setter
    def CurrentProgressValue(self, value):
        self._current_progress_value = value
        self.on_property_changed("CurrentProgressValue")

    @property
    def ResultsList(self): return self._results_list
    @ResultsList.setter
    def ResultsList(self, value):
        self._results_list = value
        self.on_property_changed("ResultsList")

    # --- Actions ---

    def run(self, parameter):
        self.StatusMessage = "Initializing operation..."
        self.IsProcessing = True
        # In a real WPF/IronPython setup, this would dispatch to a background worker.
        # For the skeleton, we mock the UI workflow popup.
        
        logger.info("Run initiated. Scope: {0}, Op: {1}".format(
            "Project" if self.ScopeEntireProject else "View",
            "CrossCheck" if self.OperationCrossCheck else "Set"
        ))
        
        # When execution completes:
        # If CrossCheck, we open ResultsDialog
        if self.OperationCrossCheck:
            self.StatusMessage = "Cross Check completed. Awaiting review."
            # Typically:
            # results_vm = ResultsViewModel(results)
            # dialog = ResultsDialog(results_vm)
            # dialog.ShowDialog()
            pass
        else:
            self.StatusMessage = "Set Room Dimensions completed successfully."
            
        self.IsProcessing = False

    def cancel(self, parameter):
        self.StatusMessage = "Operation cancelled."
        
    def export_csv(self, parameter):
        self.StatusMessage = "Exporting CSV..."
        
    def export_excel(self, parameter):
        self.StatusMessage = "Exporting Excel..."
        
    def export_json(self, parameter):
        self.StatusMessage = "Exporting JSON..."
        
    def copy_summary(self, parameter):
        self.StatusMessage = "Summary copied to clipboard."
        
    def open_folder(self, parameter):
        self.StatusMessage = "Opening Report Folder..."
        
    def settings(self, parameter):
        self.StatusMessage = "Opening Settings..."
        
    def help(self, parameter):
        self.StatusMessage = "Opening Documentation..."
