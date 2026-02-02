"""Product service - business logic for product operations"""
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, desc, text
from sqlalchemy.orm import selectinload
from app.models import Product, Category, StoreProduct
from app.api.v1.schemas.catalog import ProductCreate, ProductUpdate
from decimal import Decimal


class ProductService:
    """Product management service"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_product(self, product_data: ProductCreate) -> Product:
        """Create a new product"""
        # Create product with search vector update
        product = Product(
            name=product_data.name,
            description=product_data.description,
            category_id=product_data.category_id,
            base_price=product_data.base_price,
            unit=product_data.unit,
            image_url=product_data.image_url,
            variants=product_data.variants or {},
            is_active=product_data.is_active
        )
        
        self.db.add(product)
        await self.db.flush()
        
        product_id = product.id
        
        # Update search vector
        await self._update_search_vector(product_id)
        await self.db.commit()
        
        # Re-fetch product with eager-loaded relationships for serialization
        result = await self.db.execute(
            select(Product)
            .options(selectinload(Product.category))
            .where(Product.id == product_id)
        )
        product = result.scalar_one()
        
        return product
    
    async def get_product(self, product_id: str) -> Optional[Product]:
        """Get product by ID with category"""
        result = await self.db.execute(
            select(Product)
            .options(selectinload(Product.category))
            .where(Product.id == product_id)
        )
        return result.scalar_one_or_none()
    
    async def update_product(self, product_id: str, product_data: ProductUpdate) -> Optional[Product]:
        """Update product"""
        product = await self.get_product(product_id)
        if not product:
            return None
        
        # Update only provided fields
        update_data = product_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(product, field, value)
        
        await self.db.flush()
        
        # Update search vector if name or description changed
        if 'name' in update_data or 'description' in update_data:
            await self._update_search_vector(product_id)
        
        await self.db.commit()
        
        # Re-fetch product with eager-loaded relationships for serialization
        result = await self.db.execute(
            select(Product)
            .options(selectinload(Product.category))
            .where(Product.id == product_id)
        )
        product = result.scalar_one_or_none()
        
        return product
    
    async def delete_product(self, product_id: str) -> bool:
        """Soft delete product"""
        product = await self.get_product(product_id)
        if not product:
            return False
        
        product.is_active = False
        await self.db.commit()
        return True
    
    async def list_products(
        self,
        category_id: Optional[str] = None,
        min_price: Optional[Decimal] = None,
        max_price: Optional[Decimal] = None,
        is_active: Optional[bool] = True,
        page: int = 1,
        page_size: int = 20
    ) -> tuple[List[Product], int]:
        """List products with filters and pagination"""
        # Build query with filters
        query = select(Product).options(selectinload(Product.category))
        
        conditions = []
        if category_id:
            conditions.append(Product.category_id == category_id)
        if min_price is not None:
            conditions.append(Product.base_price >= min_price)
        if max_price is not None:
            conditions.append(Product.base_price <= max_price)
        if is_active is not None:
            conditions.append(Product.is_active == is_active)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        # Get total count
        count_query = select(func.count()).select_from(Product)
        if conditions:
            count_query = count_query.where(and_(*conditions))
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # Apply pagination
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size).order_by(desc(Product.created_at))
        
        result = await self.db.execute(query)
        products = result.scalars().all()
        
        return products, total
    
    async def search_products(
        self,
        search_query: str,
        category_id: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> tuple[List[Product], int]:
        """Full-text search for products"""
        # Use PostgreSQL full-text search
        # Convert search query to tsquery format
        search_terms = ' & '.join(search_query.split())
        
        query = select(Product).options(selectinload(Product.category))
        
        conditions = [
            func.to_tsvector('english', Product.name + ' ' + func.coalesce(Product.description, ''))
            .op('@@')(func.to_tsquery('english', search_terms))
        ]
        
        if category_id:
            conditions.append(Product.category_id == category_id)
        conditions.append(Product.is_active == True)
        
        query = query.where(and_(*conditions))
        
        # Rank results by relevance
        rank = func.ts_rank(
            func.to_tsvector('english', Product.name + ' ' + func.coalesce(Product.description, '')),
            func.to_tsquery('english', search_terms)
        )
        
        # Get total count
        count_query = select(func.count()).select_from(Product).where(and_(*conditions))
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # Apply pagination and ranking
        offset = (page - 1) * page_size
        query = query.order_by(desc(rank)).offset(offset).limit(page_size)
        
        result = await self.db.execute(query)
        products = result.scalars().all()
        
        return products, total
    
    async def _update_search_vector(self, product_id: str):
        """Update search vector for a product"""
        # This will be handled by a PostgreSQL trigger in production
        # For now, we'll compute it manually
        await self.db.execute(
            text(
                """
                UPDATE products
                SET search_vector = to_tsvector('english', name || ' ' || COALESCE(description, ''))
                WHERE id = :product_id
                """
            ),
            {"product_id": product_id}
        )
