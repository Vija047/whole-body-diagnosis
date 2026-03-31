"""
Logging configuration for production environment.
"""

import logging
import logging.handlers
import os
from pathlib import Path
from config import get_settings

settings = get_settings()


def setup_logging():
    """Configure structured logging for the application."""
    
    log_dir = Path(settings.LOG_DIR)
    log_dir.mkdir(exist_ok=True)
    
    # Create logger
    logger = logging.getLogger("mlops_api")
    logger.setLevel(getattr(logging, settings.LOG_LEVEL))
    
    # Remove existing handlers
    logger.handlers = []
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, settings.LOG_LEVEL))
    
    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        log_dir / "api.log",
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    
    # Prediction logging (separate file for audit trail)
    prediction_handler = logging.handlers.RotatingFileHandler(
        log_dir / "predictions.log",
        maxBytes=10485760,
        backupCount=10
    )
    prediction_handler.setLevel(logging.INFO)
    
    # Formatter with ISO timestamp
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    prediction_handler.setFormatter(formatter)
    
    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    # Separate logger for predictions
    pred_logger = logging.getLogger("predictions")
    pred_logger.setLevel(logging.INFO)
    pred_logger.handlers = []
    pred_logger.addHandler(prediction_handler)
    
    return logger, pred_logger


# Initialize loggers
app_logger, pred_logger = setup_logging()
