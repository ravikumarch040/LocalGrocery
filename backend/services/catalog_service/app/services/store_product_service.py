"""Store product service - store-specific product data"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from sqlalchemy.orm import selectinload, joinedload
from app.models import StoreProduct, Product, Category
from app.api.v1.schemas.catalog import StoreProductCreate, StoreProductUpdate


class StoreProductService:
    """Store product management service"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    def _serialize_store_product_with_product(self, sp: StoreProduct, product: Optional[Product] = None, category: Optional[Category] = None) -> dict:
        """Convert a StoreProduct ORM object to a serializable dict with pre-loaded relationships"""
        result = {
            'id': str(sp.id),
            'store_id': str(sp.store_id),
            'product_id': str(sp.product_id),
            'stock_quantity': sp.stock_quantity,
            'store_price': float(sp.store_price) if sp.store_price else None,
            'is_available': sp.is_available,
            'created_at': sp.created_at,
            'updated_at': sp.updated_at,
            'product': None
        }
        
        if product:
            product_dict = {
                'id': str(product.id),
                'name': product.name,
                'description': product.description,
                'category_id': str(product.category_id),
                'base_price': float(product.base_price),
                'unit': product.unit,
                'image_url': product.image_url,
                'variants': product.variants,
                'is_active': product.is_active,
                'created_at': product.created_at,
                'updated_at': product.updated_at,
                'category': None
            }
            
            if category:
                product_dict['category'] = {
                    'id': str(category.id),
                    'name': category.name,
                    'slug': category.slug,
                    'description': category.description,
                    'parent_id': str(category.parent_id) if category.parent_id else None,
                    'icon_url': category.icon_url,
                    'display_order': category.display_order,
                    'is_active': category.is_active,
                    'created_at': category.created_at,
                    'updated_at': category.updated_at
                }
            
            result['product'] = product_dict
        
        return result
    
    async def add_product_to_store(
        self,
        product_data: StoreProductCreate
    ) -> StoreProduct:
        """Associate a product with a store"""
        # Check if association already exists
        existing = await self.get_store_product(product_data.store_id, product_data.product_id)
        if existing:
            raise ValueError("Product already associated with this store")
        
        store_product = StoreProduct(
            store_id=product_data.store_id,
            product_id=product_data.product_id,
            stock_quantity=product_data.stock_quantity,
            store_price=product_data.store_price,
            is_available=product_data.is_available
        )
        
        self.db.add(store_product)
        await self.db.flush()
        
        # Load the product to ensure it's in __dict__
        product_result = await self.db.execute(
            select(Product).options(selectinload(Product.category)).where(Product.id == product_data.product_id)
        )
        product_obj = product_result.scalar_one_or_none()
        
        # Set the product into the store_product's __dict__ while session is active
        if product_obj:
            store_product.__dict__['product'] = product_obj
        
        await self.db.commit()
        
        return store_product
    
    async def get_store_product(
        self,
        store_product_id_or_store_id: str,
        product_id: Optional[str] = None
    ) -> Optional[StoreProduct]:
        """Get store product by ID or by store and product IDs"""
        if product_id:
            # Query by store_id and product_id
            result = await self.db.execute(
                select(StoreProduct)
                .where(
                    and_(
                        StoreProduct.store_id == store_product_id_or_store_id,
                        StoreProduct.product_id == product_id
                    )
                )
            )
        else:
            # Query by store_product_id
            result = await self.db.execute(
                select(StoreProduct)
                .where(StoreProduct.id == store_product_id_or_store_id)
            )
        
        store_product = result.scalar_one_or_none()
        if not store_product:
            return None
        
        # Manually load the product with its category
        product_result = await self.db.execute(
            select(Product).options(selectinload(Product.category)).where(Product.id == store_product.product_id)
        )
        product_obj = product_result.scalar_one_or_none()
        
        # Set the product into the store_product's __dict__
        if product_obj:
            store_product.__dict__['product'] = product_obj
        
        return store_product
    
    async def update_store_product(
        self,
        store_product_id: str,
        update_data: StoreProductUpdate
    ) -> Optional[dict]:
        """Update store product data"""
        # Get the store product directly
        result = await self.db.execute(
            select(StoreProduct).where(StoreProduct.id == store_product_id)
        )
        store_product = result.scalar_one_or_none()
        
        if not store_product:
            return None
        
        # Update only provided fields
        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(store_product, field, value)
        
        await self.db.flush()
        
        # Load related objects before commit
        product_result = await self.db.execute(
            select(Product).where(Product.id == store_product.product_id)
        )
        product_obj = product_result.scalar_one_or_none()
        
        # Load the category if product exists
        category_obj = None
        if product_obj:
            category_result = await self.db.execute(
                select(Category).where(Category.id == product_obj.category_id)
            )
            category_obj = category_result.scalar_one_or_none()
        
        await self.db.commit()
        
        # Re-fetch store_product to get any DB-updated values (like updated_at)
        refreshed_result = await self.db.execute(
            select(StoreProduct).where(StoreProduct.id == store_product_id)
        )
        refreshed_store_product = refreshed_result.scalar_one_or_none()
        
        # Serialize with explicitly loaded objects
        return self._serialize_store_product_with_product(refreshed_store_product, product_obj, category_obj)
    
    async def remove_product_from_store(
        self,
        store_product_id: str
    ) -> bool:
        """Remove product from store (soft delete)"""
        result = await self.db.execute(
            select(StoreProduct).where(StoreProduct.id == store_product_id)
        )
        store_product = result.scalar_one_or_none()
        
        if not store_product:
            return False
        
        store_product.is_available = False
        await self.db.commit()
        return True
    
    async def list_store_products(
        self,
        store_id: str,
        is_available: Optional[bool] = True,
        category_id: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> tuple[List[StoreProduct], int]:
        """List products for a specific store"""
        query = select(StoreProduct)
        
        conditions = [StoreProduct.store_id == store_id]
        
        if is_available is not None:
            conditions.append(StoreProduct.is_available == is_available)
        
        if category_id:
            conditions.append(Product.category_id == category_id)
        
        query = query.join(Product).where(and_(*conditions))
        
        # Get total count
        from sqlalchemy import func
        count_query = select(func.count()).select_from(StoreProduct).join(Product).where(and_(*conditions))
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # Apply pagination
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        
        result = await self.db.execute(query)
        store_products = result.scalars().all()
        
        # Manually load products for each store_product
        for sp in store_products:
            product_result = await self.db.execute(
                select(Product).options(selectinload(Product.category)).where(Product.id == sp.product_id)
            )
            product_obj = product_result.scalar_one_or_none()
            if product_obj:
                sp.__dict__['product'] = product_obj
        
        return store_products, total
