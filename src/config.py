"""Structured logging configuration for 12-Factor compliance."""
import logging
import sys
import os
from typing import Any
import json
from datetime import datetime


class JSONFormatter(logging.Formatter):
    """Output logs as JSON for log aggregation."""
    
    def format(self, record: logging.LogRecord) -> str:
        log_obj = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add extra fields
        if hasattr(record, "extra"):
            log_obj.update(record.extra)
        
        # Add exception info if present
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_obj)


def setup_logging() -> logging.Logger:
    """Configure logging based on environment."""
    logger = logging.getLogger("job_agent")
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Determine log level from environment
    level = os.getenv("LOG_LEVEL", "INFO").upper()
    logger.setLevel(getattr(logging, level, logging.INFO))
    
    # Console handler with JSON formatter in production
    handler = logging.StreamHandler(sys.stdout)
    
    if os.getenv("ENV_MODE") == "production":
        handler.setFormatter(JSONFormatter())
    else:
        # Human-readable format in development
        handler.setFormatter(logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        ))
    
    logger.addHandler(handler)
    return logger


# Default logger instance
logger = setup_logging()