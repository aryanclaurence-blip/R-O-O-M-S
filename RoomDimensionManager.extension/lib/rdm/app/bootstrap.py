# -*- coding: utf-8 -*-
"""
Application Bootstrap for the Room Dimension Manager.
Responsible for Composition Root initialization, setting up the Dependency Container,
and wiring all enterprise engines together before UI launch.
"""
import logging
import os
from rdm.app.di import DependencyContainer
from rdm.configuration.models import AppConfiguration
from rdm.utils.config import ConfigurationManager
from rdm.utils.logging import setup_logging
from rdm.models.application import PluginContext

logger = logging.getLogger(__name__)

class ApplicationContext:
    """Global singleton context for the running application."""
    def __init__(self, di_container, config, plugin_ctx):
        self.di = di_container
        self.config = config
        self.plugin = plugin_ctx
        self.is_initialized = True

class ApplicationBootstrap:
    """Composition Root entry point."""
    
    @staticmethod
    def initialize():
        """
        Validates environment, configures logging, registers DI services, 
        and returns the active ApplicationContext.
        
        Returns:
            ApplicationContext: The wired application.
        """
        # 1. Configuration
        config_path = os.path.join(os.path.expandvars("%APPDATA%"), "RoomDimensionManager", "config.json")
        config_manager = ConfigurationManager(config_path)
        app_config = AppConfiguration()
        # In full implementation, config_manager populates app_config here
        
        # 2. Logging
        log_path = os.path.join(os.path.expandvars("%APPDATA%"), "RoomDimensionManager", "logs", "app.log")
        setup_logging(
            level=app_config.logging.log_level,
            log_file=log_path,
            debug_mode=app_config.developer.debug_mode
        )
        logger.info("Starting Room Dimension Manager Application Bootstrap...")
        
        # 3. Environment & Context Validation
        plugin_ctx = PluginContext()
        # In a real environment, we inject pyrevit.EXEC_PARAMS to detect Revit version
        
        # 4. Dependency Injection Container Setup
        container = DependencyContainer()
        
        # Base Registrations
        container.register_singleton(AppConfiguration, app_config)
        container.register_singleton(PluginContext, plugin_ctx)
        
        # NOTE: In the complete implementation, all Service Layer interfaces, 
        # Geometry Engines, Parameter Engines, Transaction Engines, 
        # and ViewModels would be registered here.
        # e.g. container.register_transient(IRoomService, RoomService)
        # e.g. container.register_singleton(DimensionCalculationEngine, DimensionCalculationEngine)
        
        logger.success("Application Bootstrap completed successfully.")
        
        return ApplicationContext(
            di_container=container,
            config=app_config,
            plugin_ctx=plugin_ctx
        )

class ApplicationHost:
    """Manages the application lifecycle and shutdown logic."""
    
    def __init__(self, context):
        self.context = context
        
    def shutdown(self):
        """Flushes logs, releases Revit resources, and cleans up handles."""
        logger.info("Shutting down Room Dimension Manager...")
        # Flush pending I/O operations and clear static caches here
        logging.shutdown()
