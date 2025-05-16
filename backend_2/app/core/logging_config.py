import logging
import logging.config
import os
from pathlib import Path

# Create logs directory if it doesn't exist
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "detailed": {
            "format": (
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s "
                "[%(filename)s:%(lineno)d]"
            ),
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "level": "INFO",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "detailed",
            "level": "DEBUG",
            "filename": "logs/app.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
        },
        "error_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "detailed",
            "level": "ERROR",
            "filename": "logs/error.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
        },
        "agent_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "detailed",
            "level": "INFO",
            "filename": "logs/agents.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
        },
    },
    "loggers": {
        "": {  # Root logger
            "handlers": ["console", "file"],
            "level": os.getenv("LOG_LEVEL", "INFO"),
            "propagate": True,
        },
        "app": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
        "app.agents": {
            "handlers": ["console", "agent_file"],
            "level": "INFO",
            "propagate": False,
        },
        "app.api": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
        "app.core": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
        "app.services": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
        "uvicorn": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

def setup_logging():
    """Initialize logging configuration."""
    # Create log files with appropriate permissions
    for handler in LOGGING_CONFIG["handlers"].values():
        if "filename" in handler:
            Path(handler["filename"]).parent.mkdir(parents=True, exist_ok=True)
            # Ensure log file exists and has correct permissions
            Path(handler["filename"]).touch(exist_ok=True)
            os.chmod(handler["filename"], 0o644)
    
    logging.config.dictConfig(LOGGING_CONFIG)
    logging.info("Logging system initialized")

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.
    
    Args:
        name (str): Name of the logger, typically __name__ of the module
        
    Returns:
        logging.Logger: Configured logger instance
    """
    return logging.getLogger(name)
