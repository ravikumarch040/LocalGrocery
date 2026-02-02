"""FastAPI application factory"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.api.v1.router import router as v1_router
from app.database import engine, Base

settings = get_settings()


def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="Authentication service for LocalGrocery platform",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json"
    )
    
    # CORS middleware
    # In development: allow any localhost port (for Flutter Web dev server which uses random ports)
    # In production: restrict to specific origins via environment variables
    cors_kwargs = {
        "allow_credentials": settings.CORS_ALLOW_CREDENTIALS,
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
    
    # Include routers
    app.include_router(v1_router, prefix="/api/v1")

    # Ensure tables exist at startup
    @app.on_event("startup")
    async def init_db() -> None:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    # Health check
    @app.get("/health", tags=["Health"])
    async def health_check():
        return {"status": "healthy", "service": "auth"}
    
    return app


# Create app instance
app = create_app()
