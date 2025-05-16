"""API v1 routes and endpoints."""

from fastapi import APIRouter
from .endpoints import tasks

# Create the main v1 router
router = APIRouter()

# Include sub-routers
router.include_router(
    tasks.router,
    prefix="/tasks",
    tags=["tasks"],
    responses={
        404: {"description": "Task not found"},
        500: {"description": "Internal server error"}
    }
)

# Add more routers here as needed, for example:
# router.include_router(
#     users.router,
#     prefix="/users",
#     tags=["users"]
# )

__all__ = ['router']
