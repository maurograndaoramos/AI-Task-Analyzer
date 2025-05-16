"""Basic logging middleware for the AI Task Analysis System."""

import time
import logging
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.utils import format_duration

logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    """Simple middleware for request/response logging."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process and log the request/response cycle."""
        start_time = time.time()
        
        # Log request
        logger.info(
            f"Request: {request.method} {request.url.path} "
            f"from {request.client.host}"
        )
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Log response
            logger.info(
                f"Response: {response.status_code} for {request.method} "
                f"{request.url.path} took {format_duration(duration)}"
            )
            
            # Add timing header
            response.headers["X-Response-Time"] = format_duration(duration)
            return response
            
        except Exception as e:
            # Log error
            duration = time.time() - start_time
            logger.error(
                f"Error processing {request.method} {request.url.path}: {str(e)} "
                f"after {format_duration(duration)}"
            )
            raise

def setup_middleware(app):
    """Configure middleware for the application."""
    app.add_middleware(LoggingMiddleware)
