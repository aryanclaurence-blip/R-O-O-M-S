# -*- coding: utf-8 -*-
"""
Runners for the Parameter Management Engine.
Orchestrates the high-level application workflows: Setting Dimensions and Cross Checking.
"""
import logging
from rdm.revit.interfaces import IParameterService, IRoomService, ITransactionService
from rdm.configuration.models import AppConfiguration
from rdm.parameters.models import ParameterWriteResult, CrossCheckResult, ParameterResult
from rdm.parameters.comparers import ParameterComparer
from rdm.models.rooms import RoomModel
from rdm.models.enums import ParameterStatus, ReviewReason

logger = logging.getLogger(__name__)

class SetRoomDimensionRunner:
    """Orchestrates the workflow for calculating and writing dimensions to parameters."""
    
    def __init__(
        self,
        config,
        room_service,
        param_service,
        transaction_service: ITransactionService
        # Future injection, classification_engine, calculation_engine
    ):
        self.config = config
        self.room_service = room_service
        self.param_service = param_service
        self.transaction_service = transaction_service

    def execute(self):
        """
        Executes the primary set dimension workflow.
        
        Returns:
            List[ParameterWriteResult]: The outcomes of parameter write attempts.
        """
        logger.info("Executing Set Room Dimension workflow...")
        rooms = self.room_service.get_all_valid_rooms()
        results = []
        
        def batch_action():
            success = True
            for room in rooms:
                # Mock: In a full pipeline, we'd run Geometry -> Classification -> Calculation here
                calculated_length = 10.0
                calculated_width = 10.0
                
                try:
                    self.param_service.write_dimension(room.id, self.config.parameters.length_param_name, calculated_length)
                    self.param_service.write_dimension(room.id, self.config.parameters.width_param_name, calculated_width)
                    results.append(ParameterWriteResult(room.id, success=True))
                except Exception as e:
                    logger.warning("Failed to write parameters for room {0}: {1}".format(room.number, e))
                    results.append(ParameterWriteResult(room.id, success=False, error_message=str(e)))
                    success = False # Could choose to continue on error depending on requirements
            return success

        self.transaction_service.execute_in_transaction("Set Room Dimensions", batch_action)
        return results

class CrossCheckRunner:
    """Orchestrates the QA workflow for comparing stored parameters against calculated values."""
    
    def __init__(
        self,
        config,
        room_service,
        param_service,
        comparer: ParameterComparer
        # Future injection, classification_engine, calculation_engine
    ):
        self.config = config
        self.room_service = room_service
        self.param_service = param_service
        self.comparer = comparer

    def execute(self):
        """
        Executes the read-only cross check workflow.
        
        Returns:
            List[CrossCheckResult]: Audit records for each room.
        """
        logger.info("Executing Cross Check workflow...")
        rooms = self.room_service.get_all_valid_rooms()
        audit_results = []
        
        for room in rooms:
            # Mock calculation pipeline
            calc_length = 10.0
            calc_width = 10.0
            
            # Read parameters
            stored_length = self.param_service.read_dimension(room.id, self.config.parameters.length_param_name)
            stored_width = self.param_service.read_dimension(room.id, self.config.parameters.width_param_name)
            
            # Compare
            length_status = ParameterStatus.READY if stored_length is not None else ParameterStatus.MISSING
            width_status = ParameterStatus.READY if stored_width is not None else ParameterStatus.MISSING
            
            len_comp = self.comparer.compare(self.config.parameters.length_param_name, calc_length, stored_length, length_status)
            wid_comp = self.comparer.compare(self.config.parameters.width_param_name, calc_width, stored_width, width_status)
            
            is_pass = len_comp.within_tolerance and wid_comp.within_tolerance
            
            audit = CrossCheckResult(
                room_id=room.id,
                room_number=room.number,
                room_name=room.name,
                length_comparison=len_comp,
                width_comparison=wid_comp,
                is_pass=is_pass,
                requires_review=not is_pass
            )
            
            if not is_pass:
                audit.review_reasons.append(ReviewReason.DIMENSION_MISMATCH)
                
            audit_results.append(audit)
            
        return audit_results
