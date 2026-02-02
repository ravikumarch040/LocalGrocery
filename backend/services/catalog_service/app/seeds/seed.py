"""
Database seeding script for categories and subcategories
Run this to populate the database with initial category data
"""
import asyncio
import uuid
import re
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import select
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import settings
from app.models import Category
from app.seeds.categories import CATEGORIES_DATA


def slugify(text: str) -> str:
    """Convert text to URL-friendly slug"""
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text.strip('-')


async def seed_categories(session: AsyncSession):
    """
    Seed categories and subcategories into the database
    Uses hierarchical category structure (parent_id)
    
    Args:
        session: AsyncSession for database operations
    """
    print("Starting category seeding...")
    
    display_order = 0
    
    for category_data in CATEGORIES_DATA:
        display_order += 1
        
        # Check if parent category already exists
        result = await session.execute(
            select(Category).where(Category.name == category_data["name"])
        )
        existing_category = result.scalar_one_or_none()
        
        if existing_category:
            print(f"✓ Category '{category_data['name']}' already exists, skipping...")
            parent_category = existing_category
        else:
            # Create new parent category
            parent_category = Category(
                id=uuid.uuid4(),
                name=category_data["name"],
                slug=slugify(category_data["name"]),
                description=category_data["description"],
                parent_id=None,  # Top-level category
                display_order=display_order,
                is_active=True
            )
            session.add(parent_category)
            await session.flush()  # Flush to get the category ID
            print(f"✓ Created category: {category_data['name']}")
        
        # Add subcategories (as children with parent_id)
        sub_display_order = 0
        for subcategory_name in category_data["subcategories"]:
            sub_display_order += 1
            
            # Check if subcategory already exists
            result = await session.execute(
                select(Category).where(
                    (Category.name == subcategory_name) &
                    (Category.parent_id == parent_category.id)
                )
            )
            existing_subcategory = result.scalar_one_or_none()
            
            if existing_subcategory:
                print(f"  ✓ Subcategory '{subcategory_name}' already exists")
            else:
                # Create new subcategory
                subcategory = Category(
                    id=uuid.uuid4(),
                    parent_id=parent_category.id,  # Link to parent
                    name=subcategory_name,
                    slug=slugify(f"{category_data['name']}-{subcategory_name}"),
                    display_order=sub_display_order,
                    is_active=True
                )
                session.add(subcategory)
                print(f"  ✓ Created subcategory: {subcategory_name}")
    
    # Commit all changes
    await session.commit()
    print("\n✅ Category seeding completed successfully!")
    print(f"   Total parent categories: {len(CATEGORIES_DATA)}")
    print(f"   Total subcategories: {sum(len(c['subcategories']) for c in CATEGORIES_DATA)}")


async def main():
    """
    Main entry point for seeding
    """
    # Create async engine
    engine = create_async_engine(
        settings.DATABASE_URL,
        pool_size=settings.DB_POOL_SIZE,
        max_overflow=settings.DB_MAX_OVERFLOW,
        echo=False
    )
    
    # Create session factory
    AsyncSessionLocal = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False
    )
    
    try:
        async with AsyncSessionLocal() as session:
            await seed_categories(session)
    except Exception as e:
        print(f"❌ Error during seeding: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
