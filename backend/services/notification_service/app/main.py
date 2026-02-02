"""Main FastAPI application for Notification Service"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.database import engine, Base
from app.api.v1.endpoints import notifications
from app.config import settings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events"""
    # Startup
    logger.info("Creating database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Notification Service...")
    await engine.dispose()


# Create FastAPI app
app = FastAPI(
    title="LocalGrocery Notification Service",
    description="Multi-channel notification service (SMS, Push, Email)",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(notifications.router, prefix="/v1/notifications", tags=["Notifications"])


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "notification_service",
        "version": "1.0.0",
        "fcm_enabled": settings.FCM_ENABLED,
        "msg91_enabled": settings.MSG91_ENABLED
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "LocalGrocery Notification Service",
        "version": "1.0.0",
        "docs_url": "/docs",
        "channels": ["SMS", "PUSH", "EMAIL"]
    }
