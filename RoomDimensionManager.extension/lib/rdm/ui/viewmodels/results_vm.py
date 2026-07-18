# -*- coding: utf-8 -*-
"""
ResultsViewModel for the Room Dimension Manager.
IronPython 2.7 compatible.
Handles Post-Cross Check user decisions and reporting.
"""
from rdm.ui.viewmodels.base import ObservableObject, RelayCommand
import logging

logger = logging.getLogger(__name__)

class ResultsViewModel(ObservableObject):
    def __init__(self, total_rooms, pass_count, fail_count, review_count):
        super(ResultsViewModel, self).__init__()
        
        # Metrics
        self._total_rooms = total_rooms
        self._pass_count = pass_count
        self._fail_count = fail_count
        self._review_count = review_count
        
        # Actions
        self._action_highlight = True
        self._action_overwrite = False
        self._action_cancel = False
        
        # Commands
        self.ExportCsvCommand = RelayCommand(self.export_csv)
        self.ExportExcelCommand = RelayCommand(self.export_excel)
        self.ExportJsonCommand = RelayCommand(self.export_json)
        self.CopySummaryCommand = RelayCommand(self.copy_summary)
        self.OpenFolderCommand = RelayCommand(self.open_folder)
        self.ExecuteCommand = RelayCommand(self.execute)

    # --- Properties ---
    
    @property
    def TotalRoomsText(self):
        return "Total Rooms : {0}".format(self._total_rooms)
        
    @property
    def PassText(self):
        return "PASS : {0}".format(self._pass_count)

    @property
    def FailText(self):
        return "FAIL : {0}".format(self._fail_count)
        
    @property
    def ReviewText(self):
        return "USER REVIEW : {0}".format(self._review_count)

    @property
    def ActionHighlight(self): return self._action_highlight
    @ActionHighlight.setter
    def ActionHighlight(self, value):
        self._action_highlight = value
        self.on_property_changed("ActionHighlight")

    @property
    def ActionOverwrite(self): return self._action_overwrite
    @ActionOverwrite.setter
    def ActionOverwrite(self, value):
        self._action_overwrite = value
        self.on_property_changed("ActionOverwrite")

    @property
    def ActionCancel(self): return self._action_cancel
    @ActionCancel.setter
    def ActionCancel(self, value):
        self._action_cancel = value
        self.on_property_changed("ActionCancel")

    # --- Actions ---

    def export_csv(self, parameter):
        logger.info("Exporting CSV Report...")
        
    def export_excel(self, parameter):
        logger.info("Exporting Excel Report...")
        
    def export_json(self, parameter):
        logger.info("Exporting JSON Report...")
        
    def copy_summary(self, parameter):
        logger.info("Summary copied to clipboard.")
        
    def open_folder(self, parameter):
        logger.info("Opening Report folder...")
        
    def execute(self, parameter):
        logger.info("Executing Post-Cross Check action.")
        if self.ActionHighlight:
            logger.info("Applying Graphics Overrides...")
        elif self.ActionOverwrite:
            logger.info("Overwriting Parameter Values...")
        else:
            logger.info("Action Cancelled by User.")
        
        # In a real WPF environment, we would close the Window via an event/action.
