import asyncio
from sqlalchemy import text
from app.database import engine, Base

async def fix_and_create_tables():
    """Drop stale indexes and create all tables"""
    async with engine.connect() as conn:
        # Drop stale indexes if they exist
        try:
            await conn.execute(text("DROP INDEX IF EXISTS idx_status CASCADE"))
            await conn.commit()
            print("[1] Dropped stale idx_status")
        except Exception as e:
            print(f"[1] idx_status drop error: {e}")
        
        # Drop stale indexes that might exist
        for idx in ["idx_product_inventory_store_product", "idx_reservation_store", "idx_reservation_product"]:
            try:
                await conn.execute(text(f"DROP INDEX IF EXISTS {idx} CASCADE"))
                await conn.commit()
                print(f"[*] Dropped {idx}")
            except:
                pass
    
    # Now create all tables
    async with engine.begin() as conn:
        try:
            await conn.run_sync(Base.metadata.create_all)
            print("\n[✓] All tables created successfully")
        except Exception as e:
            print(f"[✗] Table creation error: {type(e).__name__}: {e}")

asyncio.run(fix_and_create_tables())
