"""Pydantic schemas for Catalog Service"""
from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, Dict, Any, List
from datetime import datetime
from decimal import Decimal
import re
from uuid import UUID


# ==================== Standard Response ====================

class StandardResponse(BaseModel):
    """Standard API response"""
    success: bool
    message: str


# ==================== Category Schemas ====================

class CategoryBase(BaseModel):
    """Base category schema"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    parent_id: Optional[UUID] = None
    icon_url: Optional[str] = None
    display_order: int = Field(default=0, ge=0)
    is_active: bool = True


class CategoryCreate(CategoryBase):
    """Create category request"""
    slug: Optional[str] = None
    
    @model_validator(mode='after')
    def generate_slug(self):
        if not self.slug:
            base = (self.name or '').lower()
            self.slug = re.sub(r'[^a-z0-9]+', '-', base).strip('-')
        else:
            self.slug = self.slug.lower().strip()
        return self


class CategoryUpdate(BaseModel):
    """Update category request"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    parent_id: Optional[str] = None
    icon_url: Optional[str] = None
    display_order: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None


class CategoryResponse(CategoryBase):
    """Category response"""
    id: UUID
    slug: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ==================== Product Schemas ====================

class ProductBase(BaseModel):
    """Base product schema"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    category_id: UUID
    base_price: Decimal = Field(..., gt=0, max_digits=10, decimal_places=2)
    unit: Optional[str] = Field(None, max_length=50)
    image_url: Optional[str] = None
    variants: Optional[List[Dict[str, Any]] | Dict[str, Any]] = Field(default_factory=list)
    is_active: bool = True


class ProductCreate(ProductBase):
    """Create product request"""
    pass


class ProductUpdate(BaseModel):
    """Update product request"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    category_id: Optional[UUID] = None
    base_price: Optional[Decimal] = Field(None, gt=0, max_digits=10, decimal_places=2)
    unit: Optional[str] = Field(None, max_length=50)
    image_url: Optional[str] = None
    variants: Optional[List[Dict[str, Any]] | Dict[str, Any]] = None
    is_active: Optional[bool] = None


class ProductResponse(ProductBase):
    """Product response"""
    id: UUID
    created_at: datetime
    updated_at: datetime
    category: Optional[CategoryResponse] = None
    
    class Config:
        from_attributes = True


class ProductSearchResponse(BaseModel):
    """Search results with ranking"""
    products: List[ProductResponse]
    total: int
    page: int
    page_size: int


# ==================== Store Product Schemas ====================

class StoreProductBase(BaseModel):
    """Base store product schema"""
    stock_quantity: int = Field(default=0, ge=0)
    store_price: Optional[Decimal] = Field(None, gt=0, max_digits=10, decimal_places=2)
    is_available: bool = True


class StoreProductCreate(StoreProductBase):
    """Create store product association"""
    store_id: str
    product_id: str


class StoreProductUpdate(BaseModel):
    """Update store product"""
    stock_quantity: Optional[int] = Field(None, ge=0)
    store_price: Optional[Decimal] = Field(None, gt=0, max_digits=10, decimal_places=2)
    is_available: Optional[bool] = None


class StoreProductResponse(StoreProductBase):
    """Store product response"""
    id: UUID
    store_id: UUID
    product_id: UUID
    product: Optional[ProductResponse] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ==================== Common Responses ====================

class StandardResponse(BaseModel):
    """Standard API response"""
    success: bool
    message: str
    data: Optional[Any] = None
