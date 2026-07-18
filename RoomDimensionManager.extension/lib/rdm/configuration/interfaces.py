# -*- coding: utf-8 -*-
"""
Interfaces for the Configuration Engine.
Provides abstract base classes for repositories and services.
"""
from abc import ABC, abstractmethod
from rdm.configuration.models import AppConfiguration

class IConfigurationRepository(ABC):
    """Abstract interface for configuration storage mechanisms."""
    
    @abstractmethod
    def load(self):
        """
        Load configuration from the storage medium.
        
        Returns:
            AppConfiguration: The loaded configuration instance.
        """
        pass

    @abstractmethod
    def save(self, config):
        """
        Persist the configuration to the storage medium.
        
        Args:
            config (AppConfiguration): The configuration to save.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        pass

class IConfigurationService(ABC):
    """Abstract interface for the Configuration Service."""
    
    @abstractmethod
    def get_config(self):
        """
        Retrieve the current application configuration.
        
        Returns:
            AppConfiguration: The cached configuration.
        """
        pass

    @abstractmethod
    def update_config(self, config):
        """
        Update and persist the configuration.
        
        Args:
            config (AppConfiguration): The new configuration.
            
        Returns:
            bool: True if successful.
        """
        pass

    @abstractmethod
    def subscribe(self, callback):
        """
        Subscribe to configuration change events.
        
        Args:
            callback: A function taking the new AppConfiguration as an argument.
        """
        pass
        
    @abstractmethod
    def unsubscribe(self, callback):
        """
        Unsubscribe from configuration change events.
        
        Args:
            callback: The previously subscribed function.
        """
        pass
