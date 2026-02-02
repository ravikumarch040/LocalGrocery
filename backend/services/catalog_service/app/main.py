"""Main FastAPI application"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.database import engine, Base, AsyncSessionLocal
from app.api.v1.router import router as v1_router
from app.seeds import seed_categories


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for startup/shutdown events"""
    # Startup
    print("Starting Catalog Service...")
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Database tables initialized")
    
    # Seed categories if needed
    print("Seeding categories...")
    async with AsyncSessionLocal() as session:
        await seed_categories(session)
    print("Category seeding completed")
    
    yield
    # Shutdown
    print("Shutting down Catalog Service...")
    await engine.dispose()


def create_app() -> FastAPI:
    """Application factory"""
    app = FastAPI(
        title="LocalGrocery - Catalog Service",
        description="Product catalog, categories, and store inventory management",
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # CORS configuration - allow any localhost port in debug mode
    cors_kwargs = {
        "allow_credentials": True,
        "allow_methods": ["*"],
        "allow_headers": ["*"],
    }
    
    if settings.DEBUG:
        # Development: allow any localhost origin
        cors_kwargs["allow_origin_regex"] = r"http:\/\/(localhost|127\.0\.0\.1)(:\d+)?"
    else:
        # Production: allow only specific origins
        cors_kwargs["allow_origins"] = [
            "https://localgrocery.com",
            "https://www.localgrocery.com",
        ]
    
    app.add_middleware(CORSMiddleware, **cors_kwargs)
    
    # Include API routers
    app.include_router(v1_router, prefix="/api")
    
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        return {
            "status": "healthy",
            "service": "catalog-service",
            "version": "1.0.0"
        }
    
    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8002,
        reload=True
    )
