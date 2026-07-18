# -*- coding: utf-8 -*-
"""
Configuration manager for Room Dimension Manager.
Handles loading, validating, and persisting user and project settings.
"""
import os
import json
import logging

logger = logging.getLogger(__name__)

class ConfigurationManager:
    """
    Manages application configuration, reading from local JSON or pyRevit config storage.
    Ensures default fallbacks and strict type validation.
    """
    
    DEFAULT_CONFIG= {
        "tolerance_ft": 0.01,
        "length_param_name": "Length",
        "width_param_name": "Width",
        "debug_mode": False,
        "export_directory": ""
    }

    def __init__(self, config_path= None):
        """
        Initialize the ConfigurationManager.
        
        Args:
            config_path (Optional[str]): Absolute path to a JSON configuration file.
                                         If None, uses an in-memory fallback.
        """
        self._config_path = config_path
        self._settings= self.DEFAULT_CONFIG.copy()
        
        if self._config_path:
            self.load()

    def load(self):
        """
        Loads configuration from disk if the file exists.
        Missing keys are populated with defaults.
        
        Raises:
            IOError: If the configuration file cannot be read.
            json.JSONDecodeError: If the configuration file is corrupted.
        """
        if not self._config_path or not os.path.exists(self._config_path):
            logger.debug("Configuration file not found. Using defaults.")
            return

        try:
            with open(self._config_path, 'r') as f:
                data = json.load(f)
                
            # Merge loaded data over defaults safely
            for key, default_val in self.DEFAULT_CONFIG.items():
                if key in data and isinstance(data[key], type(default_val)):
                    self._settings[key] = data[key]
                elif key in data:
                    logger.warning("Type mismatch for config key '{0}'. Using default.".format(key))
                    
            logger.info("Configuration loaded from {0}".format(self._config_path))
        except Exception as e:
            logger.error("Failed to load configuration: {0}".format(e))
            raise

    def save(self):
        """
        Persists the current configuration state to disk.
        
        Raises:
            IOError: If the file cannot be written to the configured path.
        """
        if not self._config_path:
            logger.warning("No config path defined. Cannot save settings.")
            return
            
        try:
            os.makedirs(os.path.dirname(self._config_path), exist_ok=True)
            with open(self._config_path, 'w', encoding='utf-8') as f:
                json.dump(self._settings, f, indent=4)
            logger.info("Configuration saved successfully.")
        except Exception as e:
            logger.error("Failed to save configuration to {0}: {1}".format(self._config_path, e))
            raise

    def get(self, key):
        """
        Retrieve a configuration value by key.
        
        Args:
            key (str): The configuration key.
            
        Returns:
            Any: The configured value.
            
        Raises:
            KeyError: If the key does not exist in the schema.
        """
        if key not in self._settings:
            raise KeyError("Configuration key '{0}' is invalid.".format(key))
        return self._settings[key]

    def set(self, key, value):
        """
        Update a configuration value. Enforces type consistency with defaults.
        
        Args:
            key (str): The configuration key.
            value (Any): The new value.
            
        Raises:
            KeyError: If the key is invalid.
            TypeError: If the value type does not match the default schema type.
        """
        if key not in self.DEFAULT_CONFIG:
            raise KeyError("Configuration key '{0}' is invalid.".format(key))
            
        expected_type = type(self.DEFAULT_CONFIG[key])
        if not isinstance(value, expected_type):
            raise TypeError("Expected type {0} for key '{1}', got {2}.".format(expected_type.__name__, key, type(value).__name__))
            
        self._settings[key] = value
        logger.debug("Config '{0}' updated.".format(key))
