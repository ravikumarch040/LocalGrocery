"""API v1 router - aggregates all v1 endpoints"""
from fastapi import APIRouter
from app.api.v1.endpoints import auth_router

# Create main v1 router
router = APIRouter()

# Include all endpoint routers
router.include_router(auth_router)

__all__ = ["router"]
