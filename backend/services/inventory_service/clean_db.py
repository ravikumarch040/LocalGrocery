import asyncio
from sqlalchemy import text

async def clean_create():
    """Create fresh engine and create tables without cache"""
    # Import fresh
    from sqlalchemy.ext.asyncio import create_async_engine
    from app.models import Base
    from app.config import settings
    
    # Create new engine explicitly
    engine = create_async_engine(settings.DATABASE_URL)
    
    # Dispose of any existing connections
    await engine.dispose()
    
    # Create tables
    async with engine.begin() as conn:
        try:
            await conn.run_sync(Base.metadata.create_all)
            print("[✓] Tables created successfully")
        except Exception as e:
            print(f"[✗] Error: {type(e).__name__}: {str(e)[:150]}")
    
    await engine.dispose()

asyncio.run(clean_create())
