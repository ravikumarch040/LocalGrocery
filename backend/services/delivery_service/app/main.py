"""Main FastAPI application for Delivery Service"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.database import engine, Base
from app.api.v1.endpoints import deliveries, partners
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
    logger.info("Shutting down Delivery Service...")
    await engine.dispose()


# Create FastAPI app
app = FastAPI(
    title="LocalGrocery Delivery Service",
    description="Delivery partner management and order delivery tracking",
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
app.include_router(deliveries.router, prefix="/v1/deliveries", tags=["Deliveries"])
app.include_router(partners.router, prefix="/v1/partners", tags=["Delivery Partners"])


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "delivery_service",
        "version": "1.0.0"
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "LocalGrocery Delivery Service",
        "version": "1.0.0",
        "docs_url": "/docs"
    }
