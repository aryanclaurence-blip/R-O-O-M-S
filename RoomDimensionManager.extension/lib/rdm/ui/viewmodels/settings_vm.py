# -*- coding: utf-8 -*-
"""ViewModel for the Settings Window."""

class SettingsViewModel:
    """Binds configuration data to the Settings XAML."""
    
    def __init__(self):
        self._tolerance = 0.01
        
    @property
    def Tolerance(self):
        return self._tolerance
        
    @Tolerance.setter
    def Tolerance(self, value):
        self._tolerance = value
        
    def SaveCommand(self):
        """Action to persist settings."""
        pass
