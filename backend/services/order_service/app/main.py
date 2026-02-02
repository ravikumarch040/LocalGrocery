"""FastAPI main application"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.database import init_db, close_db, engine, Base
from app.api.v1.endpoints import orders


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager"""
    # Startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await init_db()
    print("✓ Order Service database initialized")
    yield
    # Shutdown
    await close_db()
    print("✓ Order Service database closed")


def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    app = FastAPI(
        title="LocalGrocery Order Service",
        description="Order management microservice",
        version="1.0.0",
        lifespan=lifespan
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    app.include_router(orders.router, prefix=settings.api_v1_prefix)
    
    # Health check
    @app.get("/health")
    async def health():
        return {"status": "ok", "service": "order-service"}
    
    return app


# Create app instance
app = create_app()
