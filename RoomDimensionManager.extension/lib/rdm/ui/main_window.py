# -*- coding: utf-8 -*-
"""Single WPF application host for the pure pyRevit extension."""
import os
from pyrevit.framework import ObservableCollection
from Autodesk.Revit.DB import StorageType, Transaction
from pyrevit import forms, revit
from rdm.geometry.bounds import calculate_from_boundary
from rdm.parameters.service import ParameterService
from rdm.reports.csv_exporter import export
from rdm.revit.room_service import RoomService


class RoomResult(object):
    def __init__(self, room, dimensions, stored_length, stored_width, result):
        self.RoomNumber = room.Number
        self.RoomName = room.Name
        self.Classification = dimensions.classification
        self.CalculatedLength = round(dimensions.length, 3)
        self.CalculatedWidth = round(dimensions.width, 3)
        self.StoredLength = "" if stored_length is None else round(stored_length, 3)
        self.StoredWidth = "" if stored_width is None else round(stored_width, 3)
        self.Result = result


class MainWindow(forms.WPFWindow):
    def __init__(self):
        xaml = os.path.join(os.path.dirname(__file__), 'views', 'MainWindow.xaml')
        forms.WPFWindow.__init__(self, xaml)
        self.rows = ObservableCollection[RoomResult]()
        self.results_grid.ItemsSource = self.rows
        self.document_label.Text = revit.doc.Title
        self._populate_parameter_lists()
        self.status.Text = "Ready. Cross Check is non-destructive."
        self.run_button.Click += self.run
        self.export_button.Click += self.export_csv
        self.settings_button.Click += self.show_settings
        self.help_button.Click += self.show_help

    def _choice(self, control):
        return str(control.SelectedItem.Content)

    def _populate_parameter_lists(self):
        """List only writable-compatible Length parameters bound to Rooms."""
        names = set()
        try:
            rooms = RoomService(revit.doc).get_rooms("Entire Project")
            for room in rooms:
                for parameter in room.Parameters:
                    if parameter.StorageType == StorageType.Double:
                        names.add(parameter.Definition.Name)
        except Exception:
            pass
        values = sorted(names)
        self.length_parameter.ItemsSource = values
        self.width_parameter.ItemsSource = values
        if "Length" in values:
            self.length_parameter.SelectedItem = "Length"
        elif values:
            self.length_parameter.SelectedIndex = 0
        if "Width" in values:
            self.width_parameter.SelectedItem = "Width"
        elif len(values) > 1:
            self.width_parameter.SelectedIndex = 1
        elif values:
            self.width_parameter.SelectedIndex = 0

    def run(self, sender, args):
        try:
            tolerance = float(self.tolerance.Text)
        except ValueError:
            forms.alert("Tolerance must be a number in feet.", title="Room Dimension Manager")
            return
        length_name = str(self.length_parameter.SelectedItem or "").strip()
        width_name = str(self.width_parameter.SelectedItem or "").strip()
        if not length_name or not width_name:
            forms.alert("Provide both parameter names.", title="Room Dimension Manager")
            return
        operation = self._choice(self.operation)
        service = RoomService(revit.doc)
        rooms = service.get_rooms(self._choice(self.scope), revit.get_selection().element_ids)
        self.rows.Clear()
        parameter_service = ParameterService()
        transaction = None
        if operation == "Set Room Dimensions":
            transaction = Transaction(revit.doc, "Set Room Dimensions")
            transaction.Start()
        try:
            for room in rooms:
                try:
                    dimensions = calculate_from_boundary(service.get_outer_boundary(room))
                    old_length = parameter_service.read(room, length_name)
                    old_width = parameter_service.read(room, width_name)
                    if transaction:
                        parameter_service.write(room, length_name, dimensions.length)
                        parameter_service.write(room, width_name, dimensions.width)
                        outcome = "Written"
                    elif old_length is None or old_width is None:
                        outcome = "Missing parameter"
                    elif abs(old_length - dimensions.length) <= tolerance and abs(old_width - dimensions.width) <= tolerance:
                        outcome = "Pass"
                    else:
                        outcome = "Mismatch"
                    self.rows.Add(RoomResult(room, dimensions, old_length, old_width, outcome))
                except Exception as error:
                    failed = type('Dimensions', (object,), {'classification': 'Error', 'length': 0, 'width': 0})()
                    self.rows.Add(RoomResult(room, failed, None, None, str(error)))
            if transaction:
                transaction.Commit()
            self.status.Text = "Processed {0} room(s).".format(self.rows.Count)
        except Exception as error:
            if transaction and transaction.HasStarted():
                transaction.RollBack()
            forms.alert(str(error), title="Room Dimension Manager")

    def export_csv(self, sender, args):
        if self.rows.Count == 0:
            forms.alert("Run an operation before exporting.", title="Room Dimension Manager")
            return
        path = forms.save_file(file_ext='csv', default_name='room-dimensions.csv')
        if path:
            export(path, self.rows)
            self.status.Text = "Report exported: {0}".format(path)

    def show_settings(self, sender, args):
        forms.alert("Settings are saved per session in this first clean build.", title="Settings")

    def show_help(self, sender, args):
        forms.alert("Cross Check reads room boundaries without modifying the model. Set Room Dimensions writes calculated values to Double/Length room parameters.", title="Help")
