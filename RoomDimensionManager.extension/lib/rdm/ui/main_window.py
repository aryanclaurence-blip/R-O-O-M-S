# -*- coding: utf-8 -*-
"""Single WPF application host for the pure pyRevit extension."""
from pyrevit import script
try:
    from rdm.config import DEVELOPER_DEBUG_MODE
except Exception:
    DEVELOPER_DEBUG_MODE = False
import os
import System
from pyrevit.framework import ObservableCollection
from Autodesk.Revit.DB import BuiltInParameter, StorageType, Transaction, FilteredElementCollector, RevitLinkInstance
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
from rdm.utils.units import UnitHelper
from rdm.utils.session import ExecutionSession
from rdm.ui.linked_dialog import LinkedModelDialog


class RoomResult(object):
    def __init__(self, room, dimensions, stored_length, stored_width, result, unit_helper, source_doc=None, is_linked=False, doc_name="Host", doc_id=""):
        self.Room = room
        self.ElementId = GetElementIdValue(room.Id)
        number = room.get_Parameter(BuiltInParameter.ROOM_NUMBER)
        name = room.get_Parameter(BuiltInParameter.ROOM_NAME)
        self.RoomNumber = number.AsString() if number and number.HasValue else ""
        self.RoomName = name.AsString() if name and name.HasValue else ""
        self.Classification = dimensions.classification
        
        # New properties for Linked Models
        self.SourceDocument = source_doc
        self.IsLinked = is_linked
        self.DocumentName = doc_name
        self.DocumentIdentifier = doc_id
        
        # Internal numerical properties for Cross Check logic
        self.CalculatedLength = dimensions.length
        self.CalculatedWidth = dimensions.width
        self.StoredLength = stored_length
        self.StoredWidth = stored_width
        
        # Presentation properties using Revit Project Units
        self.CalculatedLengthDisplay = unit_helper.format_length(self.CalculatedLength)
        self.CalculatedWidthDisplay = unit_helper.format_length(self.CalculatedWidth)
        self.StoredLengthDisplay = "" if self.StoredLength is None else unit_helper.format_length(self.StoredLength)
        self.StoredWidthDisplay = "" if self.StoredWidth is None else unit_helper.format_length(self.StoredWidth)
        self.Result = str(result).upper()
        
        if self.Result == "GEOMETRY ERROR":
            self.CalculatedLengthDisplay = "-"
            self.CalculatedWidthDisplay = "-"
        
        
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
        self.unit_helper = UnitHelper(revit.doc)
        
        self.rows = ObservableCollection[RoomResult]()
        self.results_grid.ItemsSource = self.rows
        self._selected_links = []
        self.document_label.Text = revit.doc.Title
        self._setup_ui()
        self._populate_parameter_lists()
        
    def _setup_ui(self):
        sym = self.unit_helper.name
        if sym:
            if hasattr(self, 'label_tolerance'):
                self.label_tolerance.Text = "Tolerance ({0})".format(sym)
            if hasattr(self, 'col_length'):
                self.col_length.Header = "Length ({0})".format(sym)
            if hasattr(self, 'col_width'):
                self.col_width.Header = "Width ({0})".format(sym)
        self.set_status("Ready")
        if hasattr(self, 'tolerance'):
            self.tolerance.Text = "0.00"
        self.run_button.Click += self.run
        self.highlight_button.Click += self.highlight
        self.remove_highlight_button.Click += self.remove_highlight
        self.export_button.Click += self.export_csv
        self.settings_button.Click += self.show_settings
        self.help_button.Click += self.show_help
        
        self.scope.SelectionChanged += self.on_scope_changed
        self.select_links_button.Click += self.on_select_links_clicked
        self.filter_user.Click += self.on_filter_clicked
        self.filter_rect.Click += self.on_filter_clicked
        self.filter_quad.Click += self.on_filter_clicked
        self.filter_poly.Click += self.on_filter_clicked
        self.filter_curve.Click += self.on_filter_clicked
        self.filter_clear.Click += self.on_clear_filter
        self.pick_rooms_button.Click += self.on_pick_rooms
        self.results_grid.SelectionChanged += self.on_results_selection_changed
        
        # Grid is empty on startup.

    def _choice(self, control):
        return str(control.SelectedItem.Content)

    def _populate_parameter_lists(self):
        """List only writable-compatible Length parameters bound to Rooms."""
        names = set()
        try:
            rooms = RoomService(revit.doc).get_rooms("Entire Project")
            for room in rooms:
                for parameter in room.Parameters:
                    if parameter.StorageType in [StorageType.Double, StorageType.String]:
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

    def set_status(self, message):
        count = self.rows.Count if hasattr(self, 'rows') else 0
        self.status.Text = "{} | Rooms: {}".format(message, count)

    def on_scope_changed(self, sender, args):
        scope_name = self._choice(self.scope)
        if scope_name in ["Linked Models", "All Models"]:
            self.select_links_button.Visibility = getattr(System.Windows.Visibility, "Visible", 0)
        else:
            self.select_links_button.Visibility = getattr(System.Windows.Visibility, "Collapsed", 2)
            
        if scope_name == "Current View":
            self.filter_panel.IsEnabled = True
        else:
            self.filter_panel.IsEnabled = False
            self.on_clear_filter(None, None)

    def on_filter_clicked(self, sender, args):
        for btn in [self.filter_user, self.filter_rect, self.filter_quad, self.filter_poly, self.filter_curve]:
            if btn != sender:
                btn.IsChecked = False
                
        if not sender.IsChecked:
            self.on_clear_filter(None, None)
            return

        if sender == self.filter_user:
            self.pick_rooms_button.Visibility = getattr(System.Windows.Visibility, "Visible", 0)
        else:
            self.pick_rooms_button.Visibility = getattr(System.Windows.Visibility, "Collapsed", 2)
            
        if self._get_active_filter():
            self.filter_clear.Visibility = getattr(System.Windows.Visibility, "Visible", 0)
        else:
            self.filter_clear.Visibility = getattr(System.Windows.Visibility, "Hidden", 1)

    def on_clear_filter(self, sender, args):
        for btn in [self.filter_user, self.filter_rect, self.filter_quad, self.filter_poly, self.filter_curve]:
            btn.IsChecked = False
        self.pick_rooms_button.Visibility = getattr(System.Windows.Visibility, "Collapsed", 2)
        self.filter_clear.Visibility = getattr(System.Windows.Visibility, "Hidden", 1)

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
        self.Show()

    def on_select_links_clicked(self, sender, args):
        links = list(FilteredElementCollector(revit.doc).OfClass(RevitLinkInstance))
        valid_links = [l for l in links if l.GetLinkDocument()]
        if not valid_links:
            forms.alert("No loaded linked models were found.", title="Room Dimension Manager")
            return
            
        dlg = LinkedModelDialog(os.path.join(os.path.dirname(__file__), 'views', 'LinkedModelDialog.xaml'), valid_links)
        # Restore previous selection
        for link in self._selected_links:
            for item in dlg.link_items:
                if item.Link.Id == link.Id:
                    item.IsSelected = True
        
        if dlg.ShowDialog():
            self._selected_links = dlg.selected_links
            if len(self._selected_links) == 0:
                self.select_links_button.Content = "▼ Select Models..."
            elif len(self._selected_links) == 1:
                self.select_links_button.Content = self._selected_links[0].Name
            else:
                self.select_links_button.Content = "{} Models Selected".format(len(self._selected_links))

    def on_results_selection_changed(self, sender, args):
        from System.Collections.Generic import List
        from Autodesk.Revit.DB import ElementId
        if self.results_grid.SelectedItem:
            room = self.results_grid.SelectedItem.Room
            if room and not self.results_grid.SelectedItem.IsLinked:
                try:
                    uidoc = revit.uidoc
                    uidoc.Selection.SetElementIds(List[ElementId]([room.Id]))
                except Exception:
                    pass

    def on_results_double_click(self, sender, args):
        if self.results_grid.SelectedItem:
            room = self.results_grid.SelectedItem.Room
            if room and not self.results_grid.SelectedItem.IsLinked:
                try:
                    uidoc = revit.uidoc
                    uidoc.ShowElements(room.Id)
                    
                    # More robust zoom using BoundingBox if possible
                    for uiview in uidoc.GetOpenUIViews():
                        if uiview.ViewId == uidoc.ActiveView.Id:
                            bbox = room.get_BoundingBox(uidoc.ActiveView)
                            if bbox:
                                uiview.ZoomAndCenterRectangle(bbox.Min, bbox.Max)
                            break
                except Exception:
                    pass

    def run(self, sender, args):
        import time
        start_time = time.time()
        
        self.rows.Clear()
        self.set_status("Collecting Rooms...")
        self.highlight_button.IsEnabled = False
        self.remove_highlight_button.IsEnabled = False
        System.Windows.Forms.Application.DoEvents() if hasattr(System.Windows.Forms, 'Application') else None

        scope_name = self._choice(self.scope)
        operation = self._choice(self.operation)
        docs_to_process = []
        
        # 1. Determine Documents to Process
        if scope_name in ["Current View", "Entire Project"]:
            if scope_name == "Selected Rooms":
                forms.alert("No rooms are currently selected. Click 'Pick Rooms' to select rooms from the model.", title="Room Filter")
                self.set_status("Operation Cancelled")
                return
            docs_to_process.append((revit.doc, "Host", False))
        elif scope_name in ["Linked Models", "All Models"]:
            if not self._selected_links:
                self.on_select_links_clicked(None, None)
            
            if not self._selected_links:
                self.set_status("Operation Cancelled")
                return
                
            if scope_name == "All Models":
                docs_to_process.append((revit.doc, "Host", False))
                
            for link in self._selected_links:
                docs_to_process.append((link.GetLinkDocument(), link.Name, True))
        
        if not docs_to_process:
            return

        linked_names = [d[1] for d in docs_to_process if d[2]]
        session = ExecutionSession(operation, scope_name, revit.doc.Title, linked_names)
        session.start_timer()

        # 2. Collect Rooms
        raw_rooms = []
        for doc_obj, doc_name, is_linked in docs_to_process:
            try:
                service = RoomService(doc_obj)
                actual_scope = "Entire Project" if is_linked else scope_name
                rooms = service.get_rooms(actual_scope, revit.get_selection().element_ids)
                for r in rooms:
                    raw_rooms.append((r, doc_obj, doc_name, is_linked))
            except Exception as e:
                session.log_error("Error collecting from document {}: {}".format(doc_name, e))

        # 3. Apply Local Filters
        filter_type = self._get_active_filter()
        filtered_rooms = []
        
        if not filter_type:
            filtered_rooms = raw_rooms
        elif filter_type == "User Selected":
            # BUG 1 FIX: Only use rooms currently selected in Revit. Do not query or intersect base collection.
            # Applied in actual_scope logic above for the host.
            filtered_rooms = raw_rooms
        else:
            for r_data in raw_rooms:
                try:
                    boundary = RoomService(r_data[1]).get_outer_boundary(r_data[0])
                    if RoomClassificationEngine.classify(boundary) == filter_type:
                        filtered_rooms.append(r_data)
                except Exception as e:
                    session.log_error("Error classifying room: {}".format(e))

        session.stop_timer("Room Collection")

        if not filtered_rooms:
            session.end_session()
            session.print_to_output()
            msgs = {
                "Current View": "No rooms were found in the Current View.",
                "Entire Project": "No rooms were found in the Entire Project.",
                "Linked Models": "Selected linked models contain no rooms.",
                "All Models": "No rooms were found in any model."
            }
            forms.alert(msgs.get(scope_name, "No rooms were found for the selected Processing Scope."), title="Room Dimension Manager")
            self.set_status("Completed")
            return

        self.set_status("Calculating Geometry...")
        System.Windows.Forms.Application.DoEvents() if hasattr(System.Windows.Forms, 'Application') else None
        
        session.start_timer()
        # 4. Cross Check Execution
        try:
            tolerance = self.unit_helper.parse_length(self.tolerance.Text)
            if tolerance is None:
                tolerance = 0.00
        except Exception:
            tolerance = 0.00

        length_name = str(self.length_parameter.SelectedItem or "").strip()
        width_name = str(self.width_parameter.SelectedItem or "").strip()
        length_rule = self._choice(self.length_rule)
        width_rule = self._choice(self.width_rule)
        operation = self._choice(self.operation)
        
        if not length_name or not width_name:
            forms.alert("Provide both parameter names.", title="Room Dimension Manager")
            return
            
        for r_data in filtered_rooms:
            room = r_data[0]
            doc_obj = r_data[1]
            doc_name = r_data[2]
            is_linked = r_data[3]
            doc_id = doc_obj.Title
            
            p_service = ParameterService(doc_obj)
            r_service = RoomService(doc_obj)
            
            try:
                boundary = None
                try:
                    boundary = r_service.get_outer_boundary(room)
                except Exception as e:
                    pass
                
                if DEVELOPER_DEBUG_MODE:
                    try:
                        num = room.get_Parameter(BuiltInParameter.ROOM_NUMBER)
                        if num and num.AsString() == "2":
                            print("\n=== BOUNDARY RETRIEVAL TRACE ===")
                            print("Room Number: 2")
                            print("ElementId: {}".format(room.Id.IntegerValue))
                            print("Area: {}".format(room.Area))
                            print("Location: {}".format(room.Location.Point if room.Location else "None"))
                            print("Boundary Segment Count: {}".format(len(boundary) if boundary else 0))
                            print("Boundary Retrieval Success: {}".format(bool(boundary)))
                            print("================================")
                    except Exception:
                        pass
                
                dimensions = calculate_from_boundary(boundary, length_rule, width_rule)
                old_length = p_service.read(room, length_name)
                old_width = p_service.read(room, width_name)
                
                # 4. Create RoomResult with UNKNOWN status
                result_obj = RoomResult(room, dimensions, old_length, old_width, "UNKNOWN", self.unit_helper, doc_obj, is_linked, doc_name, doc_id)
                
                # 5. Populate Results Grid
                self.rows.Add(result_obj)
                
                # 6. Evaluate PASS / FAIL
                if old_length is None or old_width is None:
                    result_obj.Result = "FAIL"
                else:
                    len_diff = abs(old_length - dimensions.length)
                    wid_diff = abs(old_width - dimensions.width)
                    eff_tol = tolerance + 1e-7
                    len_pass = len_diff <= eff_tol
                    wid_pass = wid_diff <= eff_tol
                    
                    if len_pass and wid_pass:
                        result_obj.Result = "PASS"
                    else:
                        result_obj.Result = "FAIL"
                
                # Update result color for UI binding
                colors = {
                    "PASS": "#008000",
                    "FAIL": "#E81123",
                    "UNKNOWN": "#000000"
                }
                result_obj.ResultColor = colors.get(result_obj.Result, "#000000")
            except System.Exception as error:
                session.log_error("Cross Check Error (.NET) on Room {}: {}".format(room.Id, error))
                if DEVELOPER_DEBUG_MODE:
                    import traceback
                    print("\n=== FATAL EXCEPTION TRACE (ROOM 2) ===")
                    print("Exception Type: {}".format(type(error).__name__))
                    print("Exception Message: {}".format(str(error)))
                    print("Traceback:")
                    traceback.print_exc()
                    print("======================================\n")
                continue
            except Exception as error:
                session.log_error("Cross Check Error on Room {}: {}".format(room.Id, error))
                if DEVELOPER_DEBUG_MODE:
                    import traceback
                    print("\n=== FATAL EXCEPTION TRACE (ROOM 2) ===")
                    print("Exception Type: {}".format(type(error).__name__))
                    print("Exception Message: {}".format(str(error)))
                    print("Traceback:")
                    traceback.print_exc()
                    print("======================================\n")
                continue
                
        session.stop_timer("Cross Check")
        
        # Ensure WPF dynamically evaluates the properties now that PASS/FAIL is complete
        self.results_grid.Items.Refresh()
        
        # 5. Handle "Set Room Dimensions"
        if operation == "Set Room Dimensions":
            self.set_status("Writing Parameters...")
            System.Windows.Forms.Application.DoEvents() if hasattr(System.Windows.Forms, 'Application') else None
            session.start_timer()
            parameter_service = ParameterService(revit.doc)
            transaction = Transaction(revit.doc, "Set Room Dimensions")
            transaction.Start()
            written = 0
            try:
                for row in self.rows:
                    if row.IsLinked:
                        continue
                    if row.Result in ["FAIL", "USER REVIEW"]:
                        try:
                            parameter_service.write(row.Room, length_name, row.CalculatedLength)
                            parameter_service.write(row.Room, width_name, row.CalculatedWidth)
                            row.Result = "UPDATED"
                            row.StoredLength = row.CalculatedLength
                            row.StoredWidth = row.CalculatedWidth
                            row.StoredLengthDisplay = self.unit_helper.format_length(row.CalculatedLength)
                            row.StoredWidthDisplay = self.unit_helper.format_length(row.CalculatedWidth)
                            row.ResultColor = "#008000"
                            written += 1
                        except Exception as e:
                            session.log_error("Write Error on Room {}: {}".format(row.ElementId, e))
                            row.Result = "FAILED"
                            row.ResultColor = "#E81123"
                transaction.Commit()
                self.results_grid.Items.Refresh()
            except Exception as error:
                session.log_error("Transaction Error: {}".format(error))
                if transaction and transaction.HasStarted():
                    transaction.RollBack()
                forms.alert(str(error), title="Room Dimension Manager")
                
            session.stop_timer("Parameter Writing")
            # Do NOT enable highlight automatically for Set Room Dimensions
            self.highlight_button.IsEnabled = False
            self.remove_highlight_button.IsEnabled = False
        else:
            # Enable highlight for Cross Check
            self.highlight_button.IsEnabled = True
            self.remove_highlight_button.IsEnabled = False
            
        self.set_status("Loading Results...")
        System.Windows.Forms.Application.DoEvents() if hasattr(System.Windows.Forms, 'Application') else None
        
        # Validate grid
        allowed_statuses = ["PASS", "FAIL", "UPDATED", "READ ONLY", "USER REVIEW", "GEOMETRY ERROR"]
        processed_rooms_count = len(filtered_rooms)
        
        for r in self.rows:
            if r.Result not in allowed_statuses:
                session.log_error("Invalid status '{}' on room '{}'.".format(r.Result, r.RoomName))
                r.Result = "GEOMETRY ERROR"
        
        if DEVELOPER_DEBUG_MODE:
            print("\n======================================================================")
            print("RESULT VALIDATION")
            print("======================================================================")
            print("Processed Rooms: {}".format(processed_rooms_count))
            counts = {"PASS": 0, "FAIL": 0, "UPDATED": 0, "READ ONLY": 0, "USER REVIEW": 0, "GEOMETRY ERROR": 0}
            for r in self.rows:
                counts[r.Result] = counts.get(r.Result, 0) + 1
            for key in ["PASS", "FAIL", "UPDATED", "READ ONLY", "USER REVIEW", "GEOMETRY ERROR"]:
                print("{}: {}".format(key, counts[key]))
            print("Displayed Rows: {}".format(self.rows.Count))
            
            total = sum(counts.values())
            if total != processed_rooms_count:
                print("CRITICAL ERROR: Total Validated ({}) != Processed Rooms ({})".format(total, processed_rooms_count))
            
            print("\n======================================================================")
            print("FINAL DEBUG REPORT")
            print("======================================================================")
            print("Processed Rooms : {}".format(processed_rooms_count))
            print("Displayed Rows : {}".format(self.rows.Count))
            print("PASS : {}".format(counts["PASS"]))
            print("FAIL : {}".format(counts["FAIL"]))
            print("UPDATED : {}".format(counts["UPDATED"]))
            print("READ ONLY : {}".format(counts["READ ONLY"]))
            print("USER REVIEW : {}".format(counts["USER REVIEW"]))
            print("GEOMETRY ERRORS : {}".format(counts["GEOMETRY ERROR"]))
            
        # Sort rows based on Result: FAIL > UPDATED > PASS > READ ONLY > GEOMETRY ERROR
        sort_order = {"FAIL": 0, "UPDATED": 1, "PASS": 2, "READ ONLY": 3, "GEOMETRY ERROR": 4}
        sorted_rows = sorted(self.rows, key=lambda x: sort_order.get(x.Result, 99))
        self.rows.Clear()
        for r in sorted_rows:
            self.rows.Add(r)
        
        host_rooms = sum(1 for r in self.rows if not r.IsLinked)
        linked_rooms = sum(1 for r in self.rows if r.IsLinked)
        total_rooms = self.rows.Count
        passed = sum(1 for r in self.rows if r.Result == "PASS")
        updated = sum(1 for r in self.rows if r.Result == "UPDATED")
        failed = sum(1 for r in self.rows if r.Result in ["FAIL", "FAILED"])
        user_review = sum(1 for r in self.rows if r.Result == "USER REVIEW")
        read_only = sum(1 for r in self.rows if r.Result == "READ ONLY")
        errors = sum(1 for r in self.rows if r.Result == "GEOMETRY ERROR")
        
        session.end_session()
        session.print_to_output()
        
        summary = (
            "Execution Summary\n"
            "------------------------------------------------------\n"
            "Processing Scope\n{scope}\n\n"
            "Operation\n{operation}\n\n"
            "Host Rooms: {host}\n"
            "Linked Rooms: {link}\n"
            "Total Rooms: {total}\n\n"
            "PASS: {passed}\n"
            "FAIL: {failed}\n"
            "USER REVIEW: {user_review}\n"
            "UPDATED: {updated}\n"
            "READ ONLY: {read_only}\n"
            "FAILED: {failed_writes}\n"
            "GEOMETRY ERRORS: {errors}\n\n"
            "Execution Time: {time:.2f} seconds\n"
            "------------------------------------------------------"
        ).format(
            scope=scope_name, operation=operation, host=host_rooms, link=linked_rooms, total=total_rooms,
            passed=passed, updated=updated, failed=failed, user_review=user_review, read_only=read_only, failed_writes=sum(1 for r in self.rows if r.Result == "FAILED"), errors=errors,
            time=session.timings["Total Execution"]
        )
        
        from pyrevit import script
        script.get_output().print_html("<pre>" + summary + "</pre>")
        
        self.set_status("Completed")
        if session.errors:
            self.set_status("Completed with {} errors. See log if enabled.".format(len(session.errors)))

    def highlight(self, sender, args):
        if self.rows.Count == 0:
            return
        try:
            success_count, errors = HighlightService.apply_overrides(revit.doc, revit.doc.ActiveView, self.rows)
            revit.uidoc.RefreshActiveView()
            self.remove_highlight_button.IsEnabled = True
            if success_count == 0:
                self.set_status("No rooms require highlighting.")
            else:
                self.set_status("Applying Highlights...")
        except Exception as e:
            self.set_status("Error: {}".format(e))

    def remove_highlight(self, sender, args):
        try:
            HighlightService.remove_overrides(revit.doc, revit.doc.ActiveView)
            revit.uidoc.RefreshActiveView()
            self.remove_highlight_button.IsEnabled = False
            self.highlight_button.IsEnabled = True
            self.set_status("Highlights Removed")
        except Exception as e:
            forms.alert(str(e), title="Remove Highlight Error")

    def export_csv(self, sender, args):
        if self.rows.Count == 0:
            forms.alert("Run an operation before exporting.", title="Room Dimension Manager")
            return
        path = forms.save_file(file_ext='csv')
        if path:
            export(path, self.rows, self.unit_helper)
            forms.alert("Exported correctly.", title="Room Dimension Manager")

    def show_settings(self, sender, args):
        forms.alert("Settings are currently controlled via Revit properties.", title="Room Dimension Manager")

    def show_help(self, sender, args):
        forms.alert("Room Dimension Manager reads geometric boundaries from rooms to determine their length and width. "
                    "You can filter by room shape, specify tolerance, and write dimensions back to shared parameters.", 
                    title="Room Dimension Manager Help")
