# -*- coding: utf-8 -*-
"""
Room Services for the Revit API Layer.
Handles the collection and mapping of Autodesk.Revit.DB.Architecture.Room objects
to the internal RoomModel domain contract.
"""
import logging
from rdm.revit.interfaces import IRoomService
from rdm.models.rooms import RoomModel
from rdm.models.value_objects import Identifier
from rdm.models.enums import RoomStatus
from rdm.exceptions.hierarchy import RoomException, ErrorCode

logger = logging.getLogger(__name__)

class RoomService(IRoomService):
    """
    Implementation of the IRoomService.
    Safely retrieves rooms from the active document using FilteredElementCollector.
    """
    
    def __init__(self, doc):
        """
        Initialize the RoomService.
        
        Args:
            doc (Autodesk.Revit.DB.Document): The active Revit document.
        """
        self._doc = doc

    def get_all_valid_rooms(self):
        """
        Collects all rooms in the active view/phase that are placed and enclosed.
        
        Returns:
            List[RoomModel]: Domain models representing the valid rooms.
            
        Raises:
            RoomException: If the collector fails unexpectedly.
        """
        try:
            # We use dynamic imports to avoid blowing up unit tests outside Revit
            from Autodesk.Revit.DB import FilteredElementCollector, BuiltInCategory, SpatialElement
            from Autodesk.Revit.DB.Architecture import Room
            
            logger.info("Collecting valid rooms from the active document...")
            collector = FilteredElementCollector(self._doc).OfCategory(BuiltInCategory.OST_Rooms)
            
            valid_rooms = []
            for element in collector:
                if isinstance(element, Room):
                    # Validation rules
                    if element.Area <= 0:
                        logger.debug("Skipping room {0}: Zero area.".format(element.Id))
                        continue
                    if element.Location is None:
                        logger.debug("Skipping room {0}: Unplaced.".format(element.Id))
                        continue
                        
                    # Map to domain model
                    model = RoomModel(
                        id=Identifier(str(element.Id.IntegerValue)),
                        name=element.Name,
                        number=element.Number,
                        status=RoomStatus.VALID
                    )
                    valid_rooms.append(model)
                    
            logger.success("Collected {0} valid rooms.".format(len(valid_rooms)))
            return valid_rooms
            
        except ImportError:
            logger.error("Autodesk.Revit.DB could not be imported. Are you running outside Revit?")
            return []
        except Exception as e:
            raise RoomException("Failed to collect rooms: {0}".format(e), error_code=ErrorCode.SYS_UNEXPECTED)
