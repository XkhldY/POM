"""
Logging configuration for the application
"""

import sys
import structlog
from structlog.stdlib import LoggerFactory
from structlog.processors import TimeStamper, JSONRenderer
from structlog.stdlib import filter_by_level

from app.core.config import settings


def setup_logging():
    """Setup structured logging configuration"""
    
    # Configure structlog
    structlog.configure(
        processors=[
            filter_by_level,
            TimeStamper(fmt="iso"),
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            JSONRenderer()
        ],
        context_class=dict,
        logger_factory=LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Configure standard library logging
    import logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.LOG_LEVEL.upper()),
    )
    
    # Set specific logger levels
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    
    # Create logger instance
    logger = structlog.get_logger()
    logger.info("Logging configured", level=settings.LOG_LEVEL)
    
    return logger


def get_logger(name: str = None):
    """Get a logger instance"""
    return structlog.get_logger(name)