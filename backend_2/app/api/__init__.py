"""API package for the AI Task Analysis System."""

from fastapi import APIRouter
from .v1 import router as v1_router

# Create the main API router
router = APIRouter()

# Include versioned routers
router.include_router(
    v1_router,
    prefix="/v1"
)

__all__ = ['router']
