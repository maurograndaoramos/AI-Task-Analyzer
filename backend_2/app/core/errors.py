"""Essential error types for the AI Task Analysis System."""

from typing import Any, Dict
from fastapi import Request
from fastapi.responses import JSONResponse

from app.utils import format_datetime

class TaskAnalysisError(Exception):
    """Base exception for all task analysis errors."""
    def __init__(self, message: str, status_code: int = 500):
        super().__init__(message)
        self.message = message
        self.status_code = status_code

class AgentError(TaskAnalysisError):
    """Exception for AI agent errors."""
    def __init__(self, message: str, agent_type: str):
        super().__init__(
            message=f"Agent error ({agent_type}): {message}",
            status_code=500
        )
        self.agent_type = agent_type

class ValidationError(TaskAnalysisError):
    """Exception for data validation errors."""
    def __init__(self, message: str):
        super().__init__(message=message, status_code=422)

async def error_handler(request: Request, exc: TaskAnalysisError) -> JSONResponse:
    """Handle all task analysis errors."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.__class__.__name__,
            "message": exc.message,
            "timestamp": format_datetime(),
            "path": request.url.path
        }
    )

def setup_error_handlers(app):
    """Configure error handlers for the application."""
    app.add_exception_handler(TaskAnalysisError, error_handler)
