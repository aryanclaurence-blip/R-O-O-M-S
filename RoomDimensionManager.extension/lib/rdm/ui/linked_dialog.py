# -*- coding: utf-8 -*-
"""Dialog for selecting Linked Models."""
import os
from pyrevit import forms
from pyrevit import script

class LinkItem(object):
    """View model for a linked model checkbox item."""
    def __init__(self, name, link_instance):
        self.Name = name
        self.LinkInstance = link_instance
        self.IsSelected = True
        
    # Standard properties for WPF data binding in IronPython
    @property
    def Name_prop(self): return self.Name
    @Name_prop.setter
    def Name_prop(self, value): self.Name = value
    
    @property
    def IsSelected_prop(self): return self.IsSelected
    @IsSelected_prop.setter
    def IsSelected_prop(self, value): self.IsSelected = value


class LinkedModelDialog(forms.WPFWindow):
    def __init__(self, xaml_file_name, link_instances):
        super(LinkedModelDialog, self).__init__(xaml_file_name)
        self.link_items = [LinkItem(link.Name, link) for link in link_instances]
        self.link_listbox.ItemsSource = self.link_items
        
        self.btn_select_all.Click += self.on_select_all
        self.btn_clear_all.Click += self.on_clear_all
        self.btn_ok.Click += self.on_ok
        self.btn_cancel.Click += self.on_cancel
        self.selected_links = []
        
    def on_select_all(self, sender, args):
        for item in self.link_items:
            item.IsSelected = True
        self.link_listbox.Items.Refresh()
            
    def on_clear_all(self, sender, args):
        for item in self.link_items:
            item.IsSelected = False
        self.link_listbox.Items.Refresh()
            
    def on_ok(self, sender, args):
        self.selected_links = [item.LinkInstance for item in self.link_items if item.IsSelected]
        self.DialogResult = True
        self.Close()
        
    def on_cancel(self, sender, args):
        self.DialogResult = False
        self.Close()
