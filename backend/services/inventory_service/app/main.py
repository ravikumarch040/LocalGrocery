import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db, close_db, SessionLocal, engine, Base
from app.cache import init_redis, close_redis
from app.api.v1.endpoints import inventory
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.services.inventory_service import InventoryService

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# APScheduler for background tasks
scheduler = AsyncIOScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager: startup and shutdown"""
    # Startup
    logger.info("Initializing Inventory Service...")
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        await init_db()
    except Exception as e:
        logger.warning(f"Database connection failed (MVP mode): {str(e)}")
    
    try:
        await init_redis()
    except Exception as e:
        logger.warning(f"Redis connection failed (MVP mode): {str(e)}")
    
    # Schedule background cleanup task (every 5 minutes)
    try:
        scheduler.add_job(cleanup_expired_reservations, "interval", minutes=5)
        scheduler.start()
    except Exception as e:
        logger.warning(f"Scheduler setup failed: {str(e)}")
    
    logger.info("Inventory Service started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Inventory Service...")
    try:
        scheduler.shutdown()
    except:
        pass
    
    try:
        await close_redis()
    except:
        pass
    
    try:
        await close_db()
    except:
        pass


async def cleanup_expired_reservations():
    """Background task: Clean up expired reservations"""
    async with SessionLocal() as db:
        service = InventoryService(db)
        await service.cleanup_expired_reservations()


# Create FastAPI app
app = FastAPI(
    title="LocalGrocery Inventory Service",
    description="Manage real-time inventory, stock reservations, and audit trails",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(inventory.router)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "inventory_service",
        "version": "1.0.0",
        "redis_enabled": True,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8007,
        reload=True,
    )
