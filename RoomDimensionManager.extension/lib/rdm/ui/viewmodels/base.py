# -*- coding: utf-8 -*-
"""
Base classes for the MVVM architecture.
Provides INotifyPropertyChanged support and command implementation for IronPython WPF.
"""
import clr
clr.AddReference("PresentationCore")
clr.AddReference("PresentationFramework")
clr.AddReference("WindowsBase")
clr.AddReference("System")

from System.ComponentModel import INotifyPropertyChanged, PropertyChangedEventArgs
from System.Windows.Input import ICommand
from System import Action, Func, Object

class ObservableObject(INotifyPropertyChanged):
    """
    Base class providing PropertyChanged events for data binding in WPF.
    """
    def __init__(self):
        self.PropertyChanged = None
        self._property_changed_handlers = []
        
    def add_PropertyChanged(self, handler):
        self._property_changed_handlers.append(handler)

    def remove_PropertyChanged(self, handler):
        self._property_changed_handlers.remove(handler)

    def OnPropertyChanged(self, property_name):
        """Raises the PropertyChanged event."""
        args = PropertyChangedEventArgs(property_name)
        for handler in self._property_changed_handlers:
            handler(self, args)

    # Python code uses snake_case while WPF uses the .NET event convention.
    def on_property_changed(self, property_name):
        self.OnPropertyChanged(property_name)
            
    def set_property(self, ref_name, value, property_name):
        """
        Sets a backing field value and raises OnPropertyChanged if the value changed.
        
        Args:
            ref_name: Name of the backing attribute.
            value: The new value.
            property_name: The public property name.
            
        Returns:
            bool: True if the value changed, False otherwise.
        """
        current = getattr(self, ref_name, None)
        if current != value:
            setattr(self, ref_name, value)
            self.OnPropertyChanged(property_name)
            return True
        return False

class RelayCommand(ICommand):
    """
    A command whose sole purpose is to relay its functionality to other
    objects by invoking delegates.
    """
    def __init__(self, execute_action, can_execute_func=None):
        self._execute = execute_action
        self._can_execute = can_execute_func
        self._can_execute_changed_handlers = []

    def add_CanExecuteChanged(self, handler):
        self._can_execute_changed_handlers.append(handler)

    def remove_CanExecuteChanged(self, handler):
        self._can_execute_changed_handlers.remove(handler)

    def RaiseCanExecuteChanged(self):
        """Forces the command to re-evaluate its CanExecute state."""
        import System
        args = System.EventArgs.Empty
        for handler in self._can_execute_changed_handlers:
            handler(self, args)

    def CanExecute(self, parameter):
        """Determines whether the command can execute in its current state."""
        if self._can_execute is None:
            return True
        return self._can_execute(parameter)

    def Execute(self, parameter):
        """Executes the command action."""
        self._execute(parameter)
