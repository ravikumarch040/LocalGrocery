"""Database models for Catalog Service"""
from sqlalchemy import Column, String, Boolean, DateTime, Integer, Enum as SQLEnum, Text, Numeric, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB, TSVECTOR
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from app.database import Base


class Category(Base):
    """Product category model (hierarchical)"""
    __tablename__ = "categories"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text)
    parent_id = Column(UUID(as_uuid=True), ForeignKey('categories.id'), nullable=True)
    icon_url = Column(Text)
    display_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    products = relationship("Product", back_populates="category")
    parent = relationship("Category", remote_side=[id], backref="subcategories")


class Product(Base):
    """Product model with JSONB variants"""
    __tablename__ = "products"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    category_id = Column(UUID(as_uuid=True), ForeignKey('categories.id'), nullable=False, index=True)
    base_price = Column(Numeric(10, 2), nullable=False)
    unit = Column(String(50))  # kg, liter, piece, etc.
    image_url = Column(Text)
    
    # JSONB for flexible variant storage
    variants = Column(JSONB, default=dict)  # sizes, flavors, attributes
    
    # Full-text search
    search_vector = Column(TSVECTOR)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    category = relationship("Category", back_populates="products")
    store_products = relationship("StoreProduct", back_populates="product")
    
    # Indexes
    __table_args__ = (
        Index('ix_products_search', search_vector, postgresql_using='gin'),
        Index('ix_products_category_active', category_id, is_active),
    )


class StoreProduct(Base):
    """Store-specific product data (inventory, pricing)"""
    __tablename__ = "store_products"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    store_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey('products.id'), nullable=False, index=True)
    
    # Store-specific overrides
    stock_quantity = Column(Integer, default=0)
    store_price = Column(Numeric(10, 2), nullable=True)  # Override base_price if set
    is_available = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    product = relationship("Product", back_populates="store_products")
    
    # Indexes
    __table_args__ = (
        Index('ix_store_products_store_available', store_id, is_available),
        Index('ix_store_products_unique', store_id, product_id, unique=True),
    )
