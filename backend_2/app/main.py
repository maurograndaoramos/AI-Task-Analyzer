"""Main application entry point for the AI Task Analysis System."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import router as api_router
from app.core.config import settings
from app.core.db import connect_db, disconnect_db
from app.core.logging_config import setup_logging
from app.core.middleware import setup_middleware
from app.core.errors import setup_error_handlers

# Configure logging
setup_logging()

# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="AI-powered task analysis system with multiple specialized agents"
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set up middleware
setup_middleware(app)

# Set up error handlers
setup_error_handlers(app)

# Include API routes
app.include_router(api_router, prefix=settings.API_V1_PREFIX)

@app.on_event("startup")
async def startup():
    """Connect to database on startup."""
    await connect_db()

@app.on_event("shutdown")
async def shutdown():
    """Disconnect from database on shutdown."""
    await disconnect_db()

@app.get("/health")
async def health_check():
    """Simple health check endpoint."""
    return {
        "status": "healthy",
        "version": settings.VERSION
    }
