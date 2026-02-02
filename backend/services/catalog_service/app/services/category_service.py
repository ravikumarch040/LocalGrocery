"""Category service - business logic for category operations"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.models import Category
from app.api.v1.schemas.catalog import CategoryCreate, CategoryUpdate


class CategoryService:
    """Category management service"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_category(self, category_data: CategoryCreate) -> Category:
        """Create a new category"""
        category = Category(
            name=category_data.name,
            slug=category_data.slug,
            description=category_data.description,
            parent_id=category_data.parent_id,
            icon_url=category_data.icon_url,
            display_order=category_data.display_order,
            is_active=category_data.is_active
        )
        
        self.db.add(category)
        await self.db.commit()
        await self.db.refresh(category)
        
        return category
    
    async def get_category(self, category_id: str) -> Optional[Category]:
        """Get category by ID"""
        result = await self.db.execute(
            select(Category).where(Category.id == category_id)
        )
        return result.scalar_one_or_none()
    
    async def get_category_by_slug(self, slug: str) -> Optional[Category]:
        """Get category by slug"""
        result = await self.db.execute(
            select(Category).where(Category.slug == slug)
        )
        return result.scalar_one_or_none()
    
    async def update_category(self, category_id: str, category_data: CategoryUpdate) -> Optional[Category]:
        """Update category"""
        category = await self.get_category(category_id)
        if not category:
            return None
        
        # Update only provided fields
        update_data = category_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(category, field, value)
        
        await self.db.commit()
        await self.db.refresh(category)
        
        return category
    
    async def delete_category(self, category_id: str) -> bool:
        """Soft delete category"""
        category = await self.get_category(category_id)
        if not category:
            return False
        
        category.is_active = False
        await self.db.commit()
        return True
    
    async def list_categories(
        self,
        parent_id: Optional[str] = None,
        is_active: Optional[bool] = True
    ) -> List[Category]:
        """List all categories (optionally filtered by parent)"""
        query = select(Category)
        
        conditions = []
        if parent_id is not None:
            conditions.append(Category.parent_id == parent_id)
        if is_active is not None:
            conditions.append(Category.is_active == is_active)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.order_by(Category.display_order, Category.name)
        
        result = await self.db.execute(query)
        return result.scalars().all()
