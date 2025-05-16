import time
import asyncio
from typing import Dict, Any, Optional
from functools import wraps
from datetime import datetime
import logging
from contextlib import contextmanager
import json

from app.core.logging_config import get_logger

logger = get_logger(__name__)

class PerformanceMetrics:
    """Track and store performance metrics for agent operations."""
    
    def __init__(self):
        self.metrics = {
            "agent_executions": {},
            "api_requests": {},
            "database_operations": {}
        }
    
    def record_execution(
        self,
        category: str,
        operation: str,
        duration: float,
        success: bool,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Record a single operation execution."""
        if category not in self.metrics:
            self.metrics[category] = {}
            
        if operation not in self.metrics[category]:
            self.metrics[category][operation] = {
                "total_executions": 0,
                "successful_executions": 0,
                "failed_executions": 0,
                "total_duration": 0.0,
                "min_duration": float('inf'),
                "max_duration": 0.0,
                "last_execution": None,
                "metadata": []
            }
            
        stats = self.metrics[category][operation]
        stats["total_executions"] += 1
        stats["successful_executions"] += (1 if success else 0)
        stats["failed_executions"] += (0 if success else 1)
        stats["total_duration"] += duration
        stats["min_duration"] = min(stats["min_duration"], duration)
        stats["max_duration"] = max(stats["max_duration"], duration)
        stats["last_execution"] = datetime.utcnow().isoformat()
        
        if metadata:
            stats["metadata"].append({
                "timestamp": datetime.utcnow().isoformat(),
                "duration": duration,
                "success": success,
                **metadata
            })
            # Keep only last 100 metadata entries
            stats["metadata"] = stats["metadata"][-100:]
    
    def get_metrics(self, category: Optional[str] = None) -> Dict[str, Any]:
        """Get current metrics, optionally filtered by category."""
        if category:
            return self.metrics.get(category, {})
        return self.metrics
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of all metrics."""
        summary = {}
        
        for category, operations in self.metrics.items():
            category_stats = {
                "total_executions": 0,
                "successful_executions": 0,
                "failed_executions": 0,
                "total_duration": 0.0,
                "average_duration": 0.0
            }
            
            for op_stats in operations.values():
                category_stats["total_executions"] += op_stats["total_executions"]
                category_stats["successful_executions"] += op_stats["successful_executions"]
                category_stats["failed_executions"] += op_stats["failed_executions"]
                category_stats["total_duration"] += op_stats["total_duration"]
            
            if category_stats["total_executions"] > 0:
                category_stats["average_duration"] = (
                    category_stats["total_duration"] / category_stats["total_executions"]
                )
                category_stats["success_rate"] = (
                    category_stats["successful_executions"] / category_stats["total_executions"]
                )
            
            summary[category] = category_stats
        
        return summary

# Global metrics instance
metrics = PerformanceMetrics()

@contextmanager
def track_execution(category: str, operation: str, metadata: Optional[Dict[str, Any]] = None):
    """Context manager to track execution time and success."""
    start_time = time.time()
    success = True
    try:
        yield
    except Exception as e:
        success = False
        logger.error(f"Error in {category}.{operation}: {str(e)}")
        raise
    finally:
        duration = time.time() - start_time
        metrics.record_execution(category, operation, duration, success, metadata)

def track_agent(metadata: Optional[Dict[str, Any]] = None):
    """Decorator to track agent execution metrics."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            with track_execution("agent_executions", func.__name__, metadata):
                return await func(*args, **kwargs)
        return wrapper
    return decorator

def track_api(metadata: Optional[Dict[str, Any]] = None):
    """Decorator to track API endpoint metrics."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            with track_execution("api_requests", func.__name__, metadata):
                return await func(*args, **kwargs)
        return wrapper
    return decorator

def track_db(metadata: Optional[Dict[str, Any]] = None):
    """Decorator to track database operation metrics."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            with track_execution("database_operations", func.__name__, metadata):
                return await func(*args, **kwargs)
        return wrapper
    return decorator

def log_metrics():
    """Log current performance metrics."""
    summary = metrics.get_summary()
    logger.info("Performance Metrics Summary:\n%s", json.dumps(summary, indent=2))

# Periodic metrics logging (can be called by a background task)
async def periodic_metrics_logging(interval_seconds: int = 300):
    """Periodically log metrics summary."""
    while True:
        log_metrics()
        await asyncio.sleep(interval_seconds)

# Example usage:
"""
@track_agent(metadata={"agent_type": "TaskAnalyzer"})
async def analyze_task(self, description: str):
    # Agent implementation
    pass

@track_api(metadata={"endpoint": "/tasks/"})
async def create_task(task: TaskCreate):
    # API endpoint implementation
    pass

@track_db(metadata={"operation": "insert"})
async def save_task(task_data: Dict):
    # Database operation implementation
    pass
"""
