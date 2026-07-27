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

from pf.core.queue_manager import PFQueueManager

class ParamsFlowWindow(forms.WPFWindow):
    def __init__(self):
        xaml = os.path.join(os.path.dirname(__file__), 'views', 'ParamsFlowWindow.xaml')
        forms.WPFWindow.__init__(self, xaml)
        
        self.doc = revit.doc
        self.uidoc = revit.uidoc
        self.element_service = ElementService(self.doc, self.uidoc)
        self.parameter_service = PFParameterService(self.doc)
        self.queue_manager = PFQueueManager()
        
        self.queue_items = ObservableCollection[MappingItem]()
        self.result_items = ObservableCollection[ElementResultRow]()
        
        self.queue_grid.ItemsSource = self.queue_items
        self.results_grid.ItemsSource = self.result_items
        
        # Event Wireups
        self.scope_combo.SelectionChanged += self.on_scope_changed
        self.source_cat_combo.SelectionChanged += self.on_source_category_changed
        self.target_cat_combo.SelectionChanged += self.on_target_category_changed
        self.mapping_mode_combo.SelectionChanged += self.on_mode_changed
        self.add_mapping_btn.Click += self.on_add_mapping
        self.dup_mapping_btn.Click += self.on_duplicate
        self.move_up_btn.Click += self.on_move_up
        self.move_down_btn.Click += self.on_move_down
        self.toggle_enabled_btn.Click += self.on_toggle_enabled
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
        
        # Set ItemsSource for both independent pipelines
        self.source_cat_combo.ItemsSource = cats
        self.target_cat_combo.ItemsSource = cats
        
        if "Rooms" in cats:
            self.source_cat_combo.SelectedItem = "Rooms"
        elif len(cats) > 0:
            self.source_cat_combo.SelectedIndex = 0

        if "Doors" in cats:
            self.target_cat_combo.SelectedItem = "Doors"
        elif "Rooms" in cats:
            self.target_cat_combo.SelectedItem = "Rooms"
        elif len(cats) > 0:
            self.target_cat_combo.SelectedIndex = 0

        self.refresh_source_parameters()
        self.refresh_target_parameters()

    def refresh_source_parameters(self):
        scope_name = self._choice(self.scope_combo) or "Current View"
        cat_name = self._choice(self.source_cat_combo)
        if not cat_name or cat_name == "None":
            return

        elems = self.element_service.get_elements_in_scope(scope_name, cat_name)
        cat_key = "SRC_{}_{}".format(scope_name, cat_name)
        params = self.parameter_service.discover_parameters_for_elements(elems, cat_key=cat_key)
        self.source_param_combo.ItemsSource = params
        if params:
            self.source_param_combo.SelectedIndex = 0

        if hasattr(self, 'source_elem_card_text'):
            self.source_elem_card_text.Text = "{} Elements".format(len(elems))

    def refresh_target_parameters(self):
        scope_name = self._choice(self.scope_combo) or "Current View"
        cat_name = self._choice(self.target_cat_combo)
        if not cat_name or cat_name == "None":
            return

        elems = self.element_service.get_elements_in_scope(scope_name, cat_name)
        cat_key = "TGT_{}_{}".format(scope_name, cat_name)
        params = self.parameter_service.discover_parameters_for_elements(elems, cat_key=cat_key)
        self.target_param_combo.ItemsSource = params
        if params:
            self.target_param_combo.SelectedIndex = 0

        if hasattr(self, 'target_elem_card_text'):
            self.target_elem_card_text.Text = "{} Targets".format(len(elems))

        # Populate Discovery Preview Panel with read-only element info
        self.result_items.Clear()
        for elem in elems[:20]:
            elem_id_val = elem.Id.IntegerValue if hasattr(elem.Id, 'IntegerValue') else elem.Id
            elem_name = getattr(elem, "Name", str(elem_id_val))
            fam_name = getattr(elem, "Symbol", None)
            fam_str = fam_name.Family.Name if fam_name and hasattr(fam_name, 'Family') else cat_name
            self.result_items.Add(ElementResultRow(elem, cat_name, fam_str, "-", elem_name, "-", "PREVIEW", "Read-Only Discovery"))

        duration = time.time() - t_start
        self.set_status("{} Targets Selected ({}) | Discovery Time: {:.3f}s".format(len(elems), cat_name, duration))

    def on_scope_changed(self, sender, args):
        self.refresh_categories()

    def on_source_category_changed(self, sender, args):
        self.refresh_source_parameters()

    def on_target_category_changed(self, sender, args):
        self.refresh_target_parameters()

    def on_mode_changed(self, sender, args):
        mode = self._choice(self.mapping_mode_combo)
        need_source = mode in [
            MappingType.COPY, MappingType.FIND_REPLACE, MappingType.PREFIX,
            MappingType.SUFFIX, MappingType.UPPER_CASE, MappingType.LOWER_CASE,
            MappingType.TITLE_CASE, MappingType.TRIM, MappingType.TRIM_START, MappingType.TRIM_END
        ]
        self.source_param_panel.Visibility = getattr(System.Windows.Visibility, "Visible", 0) if need_source else getattr(System.Windows.Visibility, "Collapsed", 2)
        self.static_value_panel.Visibility = getattr(System.Windows.Visibility, "Visible", 0) if mode == MappingType.STATIC else getattr(System.Windows.Visibility, "Collapsed", 2)
        self.sequence_panel.Visibility = getattr(System.Windows.Visibility, "Visible", 0) if mode == MappingType.SEQUENCE else getattr(System.Windows.Visibility, "Collapsed", 2)

    def refresh_queue_ui(self):
        self.queue_items.Clear()
        for idx, m in enumerate(self.queue_manager.get_all(), start=1):
            self.queue_items.Add(MappingItem(m, order=idx))

        stats = self.queue_manager.get_statistics()
        if hasattr(self, 'queue_stats_text'):
            self.queue_stats_text.Text = "Mappings: {} | Enabled: {} | Categories: {}".format(stats.total, stats.enabled, stats.categories)

    def on_add_mapping(self, sender, args):
        mode = self._choice(self.mapping_mode_combo)
        src_param = self._choice(self.source_param_combo)
        tgt_param = self._choice(self.target_param_combo)
        scope_name = self._choice(self.scope_combo)
        src_cat = self._choice(self.source_cat_combo)
        tgt_cat = self._choice(self.target_cat_combo)
        static_val = self.static_value_txt.Text
        seq_pat = self.seq_pattern_txt.Text
        seq_start = self.seq_start_txt.Text
        seq_step = self.seq_step_txt.Text

        if not tgt_param:
            forms.alert("Select a Target Parameter.", title="PARAMS FLOW")
            return

        mapping_obj = ParameterMapping(
            mapping_type=mode,
            source_param=src_param,
            target_param=tgt_param,
            static_value=static_val,
            seq_pattern=seq_pat,
            seq_start=seq_start,
            seq_step=seq_step,
            source_scope=scope_name,
            source_cat=src_cat,
            target_cat=tgt_cat
        )

        if self.queue_manager.is_duplicate(mapping_obj):
            forms.alert("Warning: A duplicate mapping for Target Parameter '{}' already exists in the queue.".format(tgt_param), title="PARAMS FLOW Duplicate Warning")

        self.queue_manager.add_mapping(mapping_obj)
        self.refresh_queue_ui()
        self.set_status("Added mapping: {} -> {}".format(mode, tgt_param))

    def on_duplicate(self, sender, args):
        sel = self.queue_grid.SelectedItem
        if sel and hasattr(sel, 'Mapping'):
            self.queue_manager.duplicate_mapping(sel.Mapping)
            self.refresh_queue_ui()
            self.set_status("Duplicated selected mapping")

    def on_move_up(self, sender, args):
        sel = self.queue_grid.SelectedItem
        if sel and hasattr(sel, 'Mapping'):
            self.queue_manager.move_up(sel.Mapping)
            self.refresh_queue_ui()

    def on_move_down(self, sender, args):
        sel = self.queue_grid.SelectedItem
        if sel and hasattr(sel, 'Mapping'):
            self.queue_manager.move_down(sel.Mapping)
            self.refresh_queue_ui()

    def on_toggle_enabled(self, sender, args):
        sel = self.queue_grid.SelectedItem
        if sel and hasattr(sel, 'Mapping'):
            sel.Mapping.enabled = not getattr(sel.Mapping, 'enabled', True)
            self.refresh_queue_ui()

    def on_remove_mapping(self, sender, args):
        sel = self.queue_grid.SelectedItem
        if sel and hasattr(sel, 'Mapping'):
            self.queue_manager.remove_mapping(sel.Mapping)
            self.refresh_queue_ui()
            self.set_status("Removed selected mapping")

    def on_clear_queue(self, sender, args):
        self.queue_manager.clear()
        self.refresh_queue_ui()
        self.set_status("Cleared mapping queue")

    def _element_provider(self, scope_name, cat_name):
        return self.element_service.get_elements_in_scope(scope_name, cat_name)

    def on_validate(self, sender, args):
        mappings = self.queue_manager.get_all()
        if not mappings:
            forms.alert("Mapping Queue is empty.", title="PARAMS FLOW")
            return

        from pf.core.validation_engine import PFValidationEngine
        from pf.core.preview import PFPreviewEngine

        val_engine = PFValidationEngine(self.doc)
        reports, summary = val_engine.validate_queue(mappings, self._element_provider)

        for r in reports:
            r.mapping.status = r.status

        self.refresh_queue_ui()

        preview_engine = PFPreviewEngine(self.doc)
        preview_rows = preview_engine.generate_preview(mappings, self._element_provider, limit=100)

        self.result_items.Clear()
        for row in preview_rows:
            self.result_items.Add(row)

        msg = "Validation Complete | Ready: {} | Warnings: {} | Errors: {} | Affected Targets: {} (Showing {} preview rows)".format(
            summary.ready, summary.warnings, summary.errors, summary.affected_elements, len(preview_rows)
        )
        self.set_status(msg)

    def on_repair(self, sender, args):
        mappings = self.queue_manager.get_all()
        if not mappings:
            return
        from pf.core.validation_engine import PFValidationEngine
        from pf.core.repair import RepairEngine

        val_engine = PFValidationEngine(self.doc)
        repair_eng = RepairEngine(self.doc)

        suggestions = []
        for m in mappings:
            elems = self._element_provider(m.source_scope, m.target_cat)
            report = val_engine.validate_mapping(m, elems)
            sugg = repair_eng.analyze(report)
            if sugg:
                suggestions.append("- [{}] Target Parameter '{}': {}".format(sugg.issue_type, m.target_param, sugg.suggestion_msg))

        if suggestions:
            forms.alert("Repair Suggestions:\n\n" + "\n\n".join(suggestions), title="PARAMS FLOW Repair Engine")
        else:
            forms.alert("All mappings are valid. No repair required.", title="PARAMS FLOW Repair Engine")

    def on_apply(self, sender, args):
        mappings = self.queue_manager.get_all()
        enabled_mappings = [m for m in mappings if getattr(m, 'enabled', True)]
        if not enabled_mappings:
            forms.alert("No enabled mappings in queue.", title="PARAMS FLOW")
            return

        from pf.core.validation_engine import PFValidationEngine
        from pf.core.execution_engine import PFExecutionEngine

        val_engine = PFValidationEngine(self.doc)
        reports, val_summary = val_engine.validate_queue(enabled_mappings, self._element_provider)

        if val_summary.errors > 0:
            res = forms.alert(
                "Validation found {} Error(s) in queue. Would you still like to continue and apply valid mappings?".format(val_summary.errors),
                title="PARAMS FLOW Validation Warning",
                yes=True, no=True
            )
            if not res:
                return

        self.set_status("Executing Batch Parameter Write...")
        exec_engine = PFExecutionEngine(self.doc)
        results, summary = exec_engine.execute(enabled_mappings, self._element_provider)

        self.result_items.Clear()
        for r in results:
            self.result_items.Add(r)

        summary_msg = "BATCH APPLY COMPLETE\n\nMappings Executed: {}\nElements Processed: {}\nUpdated: {}\nSkipped: {}\nFailed: {}\nElapsed Time: {:.2f}s\nSuccess Rate: {:.1f}%".format(
            summary.mappings_count, summary.processed_count, summary.updated_count, summary.skipped_count, summary.failed_count, summary.elapsed_time, summary.success_rate
        )
        self.set_status("Batch Apply Complete | Updated: {} | Skipped: {} | Failed: {} | Time: {:.2f}s".format(
            summary.updated_count, summary.skipped_count, summary.failed_count, summary.elapsed_time
        ))
        forms.alert(summary_msg, title="PARAMS FLOW Batch Summary")

    def on_save_preset(self, sender, args):
        mappings = self.queue_manager.get_all()
        if not mappings:
            forms.alert("Mapping Queue is empty.", title="PARAMS FLOW")
            return
        path = forms.save_file(file_ext='json')
        if path:
            try:
                data = [m.to_dict() for m in mappings]
                doc_title = self.doc.Title if hasattr(self.doc, 'Title') else "Revit Model"
                PresetService.save_preset(path, data, project_name=doc_title)
                forms.alert("Preset saved successfully.", title="PARAMS FLOW")
            except Exception as ex:
                forms.alert("Error saving preset: {}".format(ex), title="PARAMS FLOW Error")

    def on_load_preset(self, sender, args):
        path = forms.pick_file(file_ext='json')
        if path:
            try:
                data = PresetService.load_preset(path)
                self.queue_manager.clear()
                for d in data:
                    mapping_obj = ParameterMapping.from_dict(d)
                    self.queue_manager.add_mapping(mapping_obj)
                self.refresh_queue_ui()
                self.set_status("Loaded preset with {} mappings.".format(len(data)))
                forms.alert("Preset loaded successfully ({} mappings).".format(len(data)), title="PARAMS FLOW")
            except Exception as ex:
                forms.alert("Error importing preset file:\n\n{}".format(ex), title="PARAMS FLOW Import Error")

    def on_export_csv(self, sender, args):
        if self.result_items.Count == 0:
            forms.alert("No result rows to export. Run Validate or Apply first.", title="PARAMS FLOW")
            return
        path = forms.save_file(file_ext='csv')
        if path:
            try:
                export_pf_csv(path, list(self.result_items))
                forms.alert("Exported results CSV successfully.", title="PARAMS FLOW")
            except Exception as ex:
                forms.alert("Error exporting CSV: {}".format(ex), title="PARAMS FLOW Error")

    def on_help(self, sender, args):
        forms.alert("PARAMS FLOW v1.0.0\n\nBatch Parameter Flow, Validation, Sequence Generation & Preset Engine.\n\nPart of the ROOMS PRO Suite.", title="PARAMS FLOW Help")
