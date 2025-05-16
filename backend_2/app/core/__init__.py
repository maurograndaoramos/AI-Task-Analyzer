"""Core functionality for the AI Task Analysis System."""

from .logging_config import setup_logging, get_logger
from .db import (
    database,
    metadata,
    connect_db,
    disconnect_db,
    create_tables,
    tasks,
    agent_executions,
    agent_configs
)
from .monitoring import (
    metrics,
    track_agent,
    track_api,
    track_db,
    log_metrics,
    periodic_metrics_logging,
    PerformanceMetrics
)

__all__ = [
    # Logging
    'setup_logging',
    'get_logger',
    
    # Database
    'database',
    'metadata',
    'connect_db',
    'disconnect_db',
    'create_tables',
    'tasks',
    'agent_executions',
    'agent_configs',
    
    # Monitoring
    'metrics',
    'track_agent',
    'track_api',
    'track_db',
    'log_metrics',
    'periodic_metrics_logging',
    'PerformanceMetrics'
]

# Initialize logging when the core module is imported
setup_logging()
