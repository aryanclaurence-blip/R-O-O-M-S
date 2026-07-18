# -*- coding: utf-8 -*-
"""
Enterprise logging framework for Room Dimension Manager.
Provides standardized formatting, multiple output targets, and structured log levels.
"""
import logging
import sys
import os

# Define standard formats
FORMAT_DEFAULT = "%(asctime)s - %(name)s - [%(levelname)s] - %(message)s"
FORMAT_DEBUG = "%(asctime)s - %(name)s - [%(levelname)s] - %(pathname)s:%(lineno)d - %(message)s"

def get_logger(name):
    """
    Retrieve a configured logger for a specific module.
    
    Args:
        name (str): The module name (typically __name__).
        
    Returns:
        logging.Logger: The configured logger instance.
    """
    return logging.getLogger(name)

def setup_logging(
    level= logging.INFO, 
    log_file= None, 
    debug_mode= False
):
    """
    Initializes the enterprise logging framework.
    Configures root logger with standard handlers (Stream and optionally File).
    
    Args:
        level (Union[int, str]): Base logging level.
        log_file (Optional[str]): Absolute path to an output log file.
        debug_mode (bool): If True, uses a verbose format with file/line details.
    
    Raises:
        ValueError: If an invalid logging level is provided.
        IOError: If the specified log_file path is inaccessible.
    """
    if isinstance(level, basestring):
        level_map = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL
        }
        level = level_map.get(level.upper(), logging.INFO)

    root_logger = logging.getLogger()
    
    # Clear existing handlers to prevent duplicates during testing or reloads
    if root_logger.hasHandlers():
        del root_logger.handlers[:]

    root_logger.setLevel(level)

    log_format = FORMAT_DEBUG if debug_mode else FORMAT_DEFAULT
    formatter = logging.Formatter(log_format)

    # Standard Console Handler (pyRevit output window)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)
    root_logger.addHandler(console_handler)

    # Optional File Handler
    if log_file:
        try:
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
            file_handler.setFormatter(formatter)
            file_handler.setLevel(level)
            root_logger.addHandler(file_handler)
        except Exception as ex:
            # Fallback to console if file logging fails, but do not crash the app
            console_handler.setLevel(logging.WARNING)
            logging.warning("Failed to initialize file logger at {0}: {1}".format(log_file, ex))

    logging.info("Enterprise logging framework initialized successfully.")
