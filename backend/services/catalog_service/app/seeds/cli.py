#!/usr/bin/env python
"""
Standalone seeding script for Catalog Service
Can be run from command line: python -m app.seeds.seed
"""
import asyncio
import sys
import os

# Ensure app is in path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.database import engine, AsyncSessionLocal
from app.seeds.seed import seed_categories


async def main():
    """Run seeding"""
    print("=" * 60)
    print("LocalGrocery - Catalog Service Database Seeding")
    print("=" * 60)
    print()
    
    try:
        async with AsyncSessionLocal() as session:
            await seed_categories(session)
        print()
        print("=" * 60)
        print("✅ Seeding completed successfully!")
        print("=" * 60)
    except Exception as e:
        print()
        print("=" * 60)
        print(f"❌ Seeding failed: {str(e)}")
        print("=" * 60)
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
