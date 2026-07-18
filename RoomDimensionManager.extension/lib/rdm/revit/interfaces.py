# -*- coding: utf-8 -*-
"""
Revit API Service Layer Interfaces.
Defines strict contracts for all Revit API interactions. No Revit objects 
shall bleed through these boundaries.
"""
from abc import ABC, abstractmethod
from rdm.models.rooms import RoomModel
from rdm.models.value_objects import Identifier

class IApplicationService(ABC):
    """Interface for Revit Application interactions."""
    @abstractmethod
    def get_revit_version(self): pass

class IDocumentService(ABC):
    """Interface for active document interactions."""
    @abstractmethod
    def get_active_document_id(self): pass

class IRoomService(ABC):
    """Interface for retrieving and mapping rooms."""
    @abstractmethod
    def get_all_valid_rooms(self):
        """Collect all valid, placed, and enclosed rooms."""
        pass

class IParameterService(ABC):
    """Interface for parameter read/write operations."""
    @abstractmethod
    def write_dimension(self, element_id, param_name, value):
        """Write a float value to an element's parameter."""
        pass
        
    @abstractmethod
    def read_dimension(self, element_id, param_name):
        """Read a float value from an element's parameter."""
        pass

class IGeometryExtractionService(ABC):
    """Interface for pulling boundary geometry from rooms."""
    @abstractmethod
    def extract_room_boundary(self, room_id):
        """Extract spatial boundaries into a pure mathematical polygon."""
        pass

class ITransactionService(ABC):
    """Interface for safely wrapping Revit transactions."""
    @abstractmethod
    def execute_in_transaction(self, name, action):
        """Execute a callable within a Revit transaction context."""
        pass

class IGraphicOverrideService(ABC):
    """Interface for temporary visual overrides."""
    @abstractmethod
    def highlight_elements(self, element_ids, color_hex):
        """Apply a solid fill override to the active view."""
        pass
        
    @abstractmethod
    def clear_overrides(self):
        """Remove all temporary overrides applied by this session."""
        pass

class IUnitConversionService(ABC):
    """Interface for converting between internal Revit units and display units."""
    @abstractmethod
    def internal_to_display(self, value): pass
    
    @abstractmethod
    def display_to_internal(self, value): pass
