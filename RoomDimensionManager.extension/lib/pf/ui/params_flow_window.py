# -*- coding: utf-8 -*-
"""WPF Window Controller for PARAMS FLOW."""
import os
import System
from pyrevit import forms, revit
from pyrevit.framework import ObservableCollection

from pf.core.mapping import MappingType, ParameterMapping
from pf.core.validator import ValidationEngine
from pf.core.repair import RepairEngine
from pf.core.executor import BatchExecutor
from pf.services.element_service import ElementService
from pf.services.parameter_service import PFParameterService
from pf.services.preset_service import PresetService
from pf.models.mapping_item import MappingItem
from pf.models.element_row import ElementResultRow
from pf.utils.pf_logger import PFExecutionSession
from pf.utils.csv_exporter import export_pf_csv

class ParamsFlowWindow(forms.WPFWindow):
    def __init__(self):
        xaml = os.path.join(os.path.dirname(__file__), 'views', 'ParamsFlowWindow.xaml')
        forms.WPFWindow.__init__(self, xaml)
        
        self.doc = revit.doc
        self.uidoc = revit.uidoc
        self.element_service = ElementService(self.doc, self.uidoc)
        self.parameter_service = PFParameterService(self.doc)
        
        self.mapping_queue = []
        self.queue_items = ObservableCollection[MappingItem]()
        self.result_items = ObservableCollection[ElementResultRow]()
        
        self.queue_grid.ItemsSource = self.queue_items
        self.results_grid.ItemsSource = self.result_items
        
        # Event Wireups
        self.scope_combo.SelectionChanged += self.on_scope_changed
        self.category_combo.SelectionChanged += self.on_category_changed
        self.mapping_mode_combo.SelectionChanged += self.on_mode_changed
        self.add_mapping_btn.Click += self.on_add_mapping
        self.remove_mapping_btn.Click += self.on_remove_mapping
        self.clear_queue_btn.Click += self.on_clear_queue
        self.validate_btn.Click += self.on_validate
        self.repair_btn.Click += self.on_repair
        self.apply_btn.Click += self.on_apply
        self.load_preset_btn.Click += self.on_load_preset
        self.save_preset_btn.Click += self.on_save_preset
        self.export_csv_btn.Click += self.on_export_csv
        self.help_btn.Click += self.on_help
        
        # Initial Load
        self.refresh_categories()

    def _choice(self, combo):
        if combo and combo.SelectedItem:
            if hasattr(combo.SelectedItem, 'Content'):
                return str(combo.SelectedItem.Content)
            return str(combo.SelectedItem)
        return ""

    def set_status(self, msg):
        self.status_text.Text = msg

    def refresh_categories(self):
        scope_name = self._choice(self.scope_combo) or "Current View"
        cats = self.element_service.get_categories_in_scope(scope_name)
        self.category_combo.ItemsSource = cats
        if "Rooms" in cats:
            self.category_combo.SelectedItem = "Rooms"
        elif len(cats) > 0:
            self.category_combo.SelectedIndex = 0
        else:
            self.category_combo.ItemsSource = ["None"]
            self.category_combo.SelectedIndex = 0

    def refresh_parameters(self):
        scope_name = self._choice(self.scope_combo) or "Current View"
        cat_name = self._choice(self.category_combo)
        elems = self.element_service.get_elements_in_scope(scope_name, cat_name)
        params = self.parameter_service.discover_parameters_for_elements(elems)
        self.source_param_combo.ItemsSource = params
        self.target_param_combo.ItemsSource = params
        if params:
            self.source_param_combo.SelectedIndex = 0
            self.target_param_combo.SelectedIndex = 0 if len(params) < 2 else 1

    def on_scope_changed(self, sender, args):
        self.refresh_categories()

    def on_category_changed(self, sender, args):
        self.refresh_parameters()

    def on_mode_changed(self, sender, args):
        mode = self._choice(self.mapping_mode_combo)
        self.source_param_panel.Visibility = getattr(System.Windows.Visibility, "Visible", 0) if mode in [MappingType.COPY, MappingType.FIND_REPLACE] else getattr(System.Windows.Visibility, "Collapsed", 2)
        self.static_value_panel.Visibility = getattr(System.Windows.Visibility, "Visible", 0) if mode == MappingType.STATIC else getattr(System.Windows.Visibility, "Collapsed", 2)
        self.sequence_panel.Visibility = getattr(System.Windows.Visibility, "Visible", 0) if mode == MappingType.SEQUENCE else getattr(System.Windows.Visibility, "Collapsed", 2)

    def on_add_mapping(self, sender, args):
        mode = self._choice(self.mapping_mode_combo)
        src_param = self._choice(self.source_param_combo)
        tgt_param = self._choice(self.target_param_combo)
        static_val = self.static_value_txt.Text
        seq_pat = self.seq_pattern_txt.Text
        seq_start = self.seq_start_txt.Text
        seq_step = self.seq_step_txt.Text

        if not tgt_param:
            forms.alert("Select a Target Parameter.", title="PARAMS FLOW")
            return

        mapping_obj = ParameterMapping(mode, src_param, tgt_param, static_val, seq_pat, seq_start, seq_step)
        self.mapping_queue.append(mapping_obj)
        self.queue_items.Add(MappingItem(mapping_obj))
        self.set_status("Added mapping: {} -> {}".format(mode, tgt_param))

    def on_remove_mapping(self, sender, args):
        sel = self.queue_grid.SelectedItem
        if sel:
            self.mapping_queue.remove(sel.Mapping)
            self.queue_items.Remove(sel)
            self.set_status("Removed mapping")

    def on_clear_queue(self, sender, args):
        self.mapping_queue = []
        self.queue_items.Clear()
        self.set_status("Cleared mapping queue")

    def on_validate(self, sender, args):
        if not self.mapping_queue:
            forms.alert("Mapping Queue is empty.", title="PARAMS FLOW")
            return
        
        scope_name = self._choice(self.scope_combo)
        cat_name = self._choice(self.category_combo)
        elems = self.element_service.get_elements_in_scope(scope_name, cat_name)
        
        validator = ValidationEngine(self.doc)
        self.queue_items.Clear()
        for m in self.mapping_queue:
            res = validator.validate_mapping(m, elems)
            m.status = res.status
            self.queue_items.Add(MappingItem(m))

        self.result_items.Clear()
        for elem in elems[:10]:
            for m in self.mapping_queue:
                src_val = self.parameter_service.read_param_as_string(elem, m.source_param) if m.mapping_type == MappingType.COPY else m.static_value
                old_tgt = self.parameter_service.read_param_as_string(elem, m.target_param)
                self.result_items.Add(ElementResultRow(elem, cat_name, m.source_param or m.mapping_type, m.target_param, old_tgt, src_val, "PREVIEW", "Sample Preview"))

        self.set_status("Validation complete. Validated {} mappings across {} elements.".format(len(self.mapping_queue), len(elems)))

    def on_repair(self, sender, args):
        if not self.mapping_queue:
            return
        scope_name = self._choice(self.scope_combo)
        cat_name = self._choice(self.category_combo)
        elems = self.element_service.get_elements_in_scope(scope_name, cat_name)
        validator = ValidationEngine(self.doc)
        repair_eng = RepairEngine(self.doc)

        suggestions = []
        for m in self.mapping_queue:
            vres = validator.validate_mapping(m, elems)
            sugg = repair_eng.analyze(vres)
            if sugg:
                suggestions.append("- [{}] Target Parameter '{}': {}".format(sugg.issue_type, m.target_param, sugg.suggestion_msg))

        if suggestions:
            forms.alert("Repair Suggestions:\n\n" + "\n\n".join(suggestions), title="PARAMS FLOW Repair Engine")
        else:
            forms.alert("All mappings are valid. No repair required.", title="PARAMS FLOW Repair Engine")

    def on_apply(self, sender, args):
        if not self.mapping_queue:
            forms.alert("Mapping Queue is empty.", title="PARAMS FLOW")
            return

        scope_name = self._choice(self.scope_combo)
        cat_name = self._choice(self.category_combo)
        elems = self.element_service.get_elements_in_scope(scope_name, cat_name)
        if not elems:
            forms.alert("No elements found in selected scope/category.", title="PARAMS FLOW")
            return

        session = PFExecutionSession("Batch Apply", scope_name, cat_name)
        executor = BatchExecutor(self.doc)
        
        self.set_status("Executing batch parameter write...")
        System.Windows.Forms.Application.DoEvents() if hasattr(System.Windows.Forms, 'Application') else None

        results = executor.execute_mappings(self.mapping_queue, elems, session)

        self.result_items.Clear()
        for r in results:
            self.result_items.Add(r)

        updated_count = sum(1 for r in results if r.Status == "UPDATED")
        self.set_status("Batch Apply Complete. Updated: {} | Time: {:.2f}s".format(updated_count, session.get_duration()))
        forms.alert("Batch Apply Completed Successfully!\n\nElements Updated: {}\nExecution Time: {:.2f} seconds".format(updated_count, session.get_duration()), title="PARAMS FLOW")

    def on_save_preset(self, sender, args):
        if not self.mapping_queue:
            forms.alert("Queue is empty.", title="PARAMS FLOW")
            return
        path = forms.save_file(file_ext='json')
        if path:
            data = [m.to_dict() for m in self.mapping_queue]
            PresetService.save_preset(path, data)
            forms.alert("Preset saved successfully.", title="PARAMS FLOW")

    def on_load_preset(self, sender, args):
        path = forms.pick_file(file_ext='json')
        if path:
            data = PresetService.load_preset(path)
            self.mapping_queue = [ParameterMapping.from_dict(d) for d in data]
            self.queue_items.Clear()
            for m in self.mapping_queue:
                self.queue_items.Add(MappingItem(m))
            self.set_status("Loaded preset with {} mappings.".format(len(self.mapping_queue)))

    def on_export_csv(self, sender, args):
        if self.result_items.Count == 0:
            forms.alert("No result rows to export. Run Validate or Apply first.", title="PARAMS FLOW")
            return
        path = forms.save_file(file_ext='csv')
        if path:
            export_pf_csv(path, list(self.result_items))
            forms.alert("Exported results CSV successfully.", title="PARAMS FLOW")

    def on_help(self, sender, args):
        forms.alert("PARAMS FLOW v1.0.0\n\nBatch Parameter Flow, Validation, Sequence Generation & Preset Engine.\n\nPart of the ROOMS PRO Suite.", title="PARAMS FLOW Help")
