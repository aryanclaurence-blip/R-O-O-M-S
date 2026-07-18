# -*- coding: utf-8 -*-
"""Single WPF application host for the pure pyRevit extension."""
import os
import System
from pyrevit.framework import ObservableCollection
from Autodesk.Revit.DB import BuiltInParameter, StorageType, Transaction
from pyrevit import forms, revit
from rdm.geometry.bounds import calculate_from_boundary
from rdm.parameters.service import ParameterService
from rdm.reports.csv_exporter import export
from rdm.revit.room_service import RoomService
from rdm.classification.engine import RoomClassificationEngine
from Autodesk.Revit.UI.Selection import ObjectType
from Autodesk.Revit.DB.Architecture import Room
from rdm.revit.highlight_service import HighlightService
from rdm.utils.compat import GetElementIdValue


class RoomResult(object):
    def __init__(self, room, dimensions, stored_length, stored_width, result):
        self.Room = room
        self.ElementId = GetElementIdValue(room.Id)
        number = room.get_Parameter(BuiltInParameter.ROOM_NUMBER)
        name = room.get_Parameter(BuiltInParameter.ROOM_NAME)
        self.RoomNumber = number.AsString() if number and number.HasValue else ""
        self.RoomName = name.AsString() if name and name.HasValue else ""
        self.Classification = dimensions.classification
        self.CalculatedLength = round(dimensions.length, 3)
        self.CalculatedWidth = round(dimensions.width, 3)
        self.StoredLength = "" if stored_length is None else round(stored_length, 3)
        self.StoredWidth = "" if stored_width is None else round(stored_width, 3)
        self.Result = str(result).upper()
        
        colors = {
            "PASS": "#008000",
            "FAIL": "#E81123",
            "USER REVIEW": "#D8A41E",
            "MISSING PARAMETER": "#D83B01",
            "READ ONLY": "#005A9E",
            "GEOMETRY ERROR": "#800080"
        }
        self.ResultColor = colors.get(self.Result, "#000000")


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
        self.highlight_button.Click += self.highlight
        self.remove_highlight_button.Click += self.remove_highlight
        self.export_button.Click += self.export_csv
        self.settings_button.Click += self.show_settings
        self.help_button.Click += self.show_help
        
        self.scope.SelectionChanged += self.on_scope_changed
        self.filter_user.Click += self.on_filter_clicked
        self.filter_rect.Click += self.on_filter_clicked
        self.filter_quad.Click += self.on_filter_clicked
        self.filter_poly.Click += self.on_filter_clicked
        self.filter_curve.Click += self.on_filter_clicked
        self.filter_clear.Click += self.on_clear_filter
        self.pick_rooms_button.Click += self.on_pick_rooms
        
        self._all_rooms = []
        self._collect_base_rooms()
        self._refresh_grid()

    def _collect_base_rooms(self):
        service = RoomService(revit.doc)
        self._all_rooms = service.get_rooms(self._choice(self.scope), revit.get_selection().element_ids)

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

    def _get_active_filter(self):
        if self.filter_user.IsChecked: return "User Selected"
        if self.filter_rect.IsChecked: return "Perfect Rectangle"
        if self.filter_quad.IsChecked: return "Four-Sided Non-Rectangle"
        if self.filter_poly.IsChecked: return "Complex Polygon"
        if self.filter_curve.IsChecked: return "Curved Geometry"
        return None

    def on_scope_changed(self, sender, args):
        if self._choice(self.scope) == "Entire Project":
            self.filter_panel.IsEnabled = False
            self.on_clear_filter(None, None)
        else:
            self.filter_panel.IsEnabled = True
            self._collect_base_rooms()
            self._refresh_grid()

    def on_filter_clicked(self, sender, args):
        for btn in [self.filter_user, self.filter_rect, self.filter_quad, self.filter_poly, self.filter_curve]:
            if btn != sender:
                btn.IsChecked = False
                
        if not sender.IsChecked:
            self.on_clear_filter(None, None)
            return

        if sender == self.filter_user:
            if not revit.get_selection().element_ids:
                forms.alert("No rooms are currently selected.\n\nClick 'Pick Rooms' to select rooms from the model.", title="Room Filter")
                self.pick_rooms_button.Visibility = getattr(System.Windows.Visibility, "Visible", 0) # Fallback if enum fails
                self.pick_rooms_button.Visibility = System.Windows.Visibility.Visible
                sender.IsChecked = False
                self._refresh_grid()
                return
                
        self.pick_rooms_button.Visibility = System.Windows.Visibility.Collapsed
        self._refresh_grid()

    def on_clear_filter(self, sender, args):
        for btn in [self.filter_user, self.filter_rect, self.filter_quad, self.filter_poly, self.filter_curve]:
            btn.IsChecked = False
        self.pick_rooms_button.Visibility = System.Windows.Visibility.Collapsed
        self._refresh_grid()

    def on_pick_rooms(self, sender, args):
        self.Hide()
        try:
            selected = revit.uidoc.Selection.PickObjects(ObjectType.Element, "Select Rooms")
            new_ids = [ref.ElementId for ref in selected]
            revit.get_selection().set_to(new_ids)
            self.filter_user.IsChecked = True
            self.on_filter_clicked(self.filter_user, None)
        except Exception:
            pass
        finally:
            self.ShowDialog()

    def _refresh_grid(self, sender=None, args=None):
        try:
            tolerance = float(self.tolerance.Text)
        except ValueError:
            tolerance = 0.01

        length_name = str(self.length_parameter.SelectedItem or "").strip()
        width_name = str(self.width_parameter.SelectedItem or "").strip()
        length_rule = self._choice(self.length_rule)
        width_rule = self._choice(self.width_rule)
        
        filter_type = self._get_active_filter()
        filtered_rooms = []
        
        if not filter_type:
            filtered_rooms = list(self._all_rooms)
        elif filter_type == "User Selected":
            # BUG 1 FIX: Only use rooms currently selected in Revit. Do not query or intersect base collection.
            for eid in revit.get_selection().element_ids:
                element = revit.doc.GetElement(eid)
                if isinstance(element, Room):
                    filtered_rooms.append(element)
        else:
            service = RoomService(revit.doc)
            for room in self._all_rooms:
                try:
                    boundary = service.get_outer_boundary(room)
                    cls = RoomClassificationEngine.classify(boundary)
                    if cls == filter_type:
                        filtered_rooms.append(room)
                except Exception:
                    pass

        self.rooms_found_text.Text = "Rooms Found: {0}".format(len(filtered_rooms))
        self.rows.Clear()
        
        if not length_name or not width_name:
            return

        parameter_service = ParameterService()
        service = RoomService(revit.doc)
        for room in filtered_rooms:
            try:
                dimensions = calculate_from_boundary(service.get_outer_boundary(room), length_rule, width_rule)
                old_length = parameter_service.read(room, length_name)
                old_width = parameter_service.read(room, width_name)
                
                p_len = room.LookupParameter(length_name)
                p_wid = room.LookupParameter(width_name)
                
                if p_len is None or p_wid is None:
                    outcome = "MISSING PARAMETER"
                elif p_len.IsReadOnly or p_wid.IsReadOnly:
                    outcome = "READ ONLY"
                elif old_length is None or old_width is None:
                    outcome = "MISSING PARAMETER"
                elif abs(old_length - dimensions.length) > tolerance or abs(old_width - dimensions.width) > tolerance:
                    outcome = "FAIL"
                elif dimensions.classification in ["Complex Polygon", "Ambiguous Geometry"]:
                    outcome = "USER REVIEW"
                else:
                    outcome = "PASS"
                    
                self.rows.Add(RoomResult(room, dimensions, old_length, old_width, outcome))
            except Exception as error:
                failed = type('Dimensions', (object,), {'classification': 'Error', 'length': 0, 'width': 0})()
                self.rows.Add(RoomResult(room, failed, None, None, "GEOMETRY ERROR"))

        status_scope = self._choice(self.scope)
        status_filter = filter_type if filter_type else "None"
        self.status.Text = "Ready | Scope: {0} | Filter: {1} | Rooms: {2}".format(status_scope, status_filter, len(filtered_rooms))
        
        # Reset Highlight button state
        self.highlight_button.IsEnabled = False
        self.remove_highlight_button.IsEnabled = False

    def run(self, sender, args):
        operation = self._choice(self.operation)
        if operation == "Cross Check":
            self.status.Text = "Cross check complete. {0} room(s) evaluated.".format(self.rows.Count)
            self.highlight_button.IsEnabled = True
            return

        length_name = str(self.length_parameter.SelectedItem or "").strip()
        width_name = str(self.width_parameter.SelectedItem or "").strip()
        if not length_name or not width_name:
            forms.alert("Provide both parameter names.", title="Room Dimension Manager")
            return
            
        parameter_service = ParameterService()
        transaction = Transaction(revit.doc, "Set Room Dimensions")
        transaction.Start()
        written = 0
        try:
            for row in self.rows:
                if row.Result == "Mismatch" or row.Result == "Missing parameter":
                    parameter_service.write(row.Room, length_name, row.CalculatedLength)
                    parameter_service.write(row.Room, width_name, row.CalculatedWidth)
                    row.Result = "Written"
                    row.StoredLength = row.CalculatedLength
                    row.StoredWidth = row.CalculatedWidth
                    written += 1
                    
            transaction.Commit()
            self.status.Text = "Processed {0} room(s). Wrote {1} parameters.".format(self.rows.Count, written)
        except Exception as error:
            if transaction and transaction.HasStarted():
                transaction.RollBack()
            forms.alert(str(error), title="Room Dimension Manager")

    def highlight(self, sender, args):
        if self.rows.Count == 0:
            return
        try:
            HighlightService.apply_overrides(revit.doc, revit.doc.ActiveView, self.rows)
            self.remove_highlight_button.IsEnabled = True
            self.highlight_button.IsEnabled = False
            self.status.Text = "Highlights applied to {0} rooms.".format(self.rows.Count)
        except Exception as e:
            forms.alert(str(e), title="Highlight Error")

    def remove_highlight(self, sender, args):
        if self.rows.Count == 0:
            return
        try:
            HighlightService.remove_overrides(revit.doc, revit.doc.ActiveView, self.rows)
            self.remove_highlight_button.IsEnabled = False
            self.highlight_button.IsEnabled = True
            self.status.Text = "Highlights removed."
        except Exception as e:
            forms.alert(str(e), title="Remove Highlight Error")

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
