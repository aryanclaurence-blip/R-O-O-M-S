# -*- coding: utf-8 -*-
"""Reporting models and CSV Exporters."""
import logging
import csv

logger = logging.getLogger(__name__)

class CSVExporter:
    """Generates CSV files for QA reporting."""
    
    def export(self, filepath, data):
        """
        Write the cross-check results to a CSV file.
        
        Args:
            filepath (str): Output location.
            data (List[Dict[str, Any]]): Serialized QA data.
            
        Returns:
            bool: True if write succeeded.
        """
        if not data:
            return False
        with open(filepath, 'wb') as stream:
            writer = csv.DictWriter(stream, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        logger.info("Exported report to {0}".format(filepath))
        return True
