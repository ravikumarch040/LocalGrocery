from sqlalchemy import Column, String, UUID, DateTime, Float, Integer, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from uuid import uuid4
from app.database import Base


class Cart(Base):
    """Shopping cart for a customer"""
    __tablename__ = "carts"
    
    id = Column(UUID, primary_key=True)
    customer_id = Column(String(255), nullable=False, index=True)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    expires_at = Column(DateTime, nullable=True)  # Cart expiration time
    
    # Relationships
    items = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Cart(id={self.id}, customer_id={self.customer_id}, items={len(self.items)})>"
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "customer_id": self.customer_id,
            "items_count": len(self.items),
            "total_items": sum(item.quantity for item in self.items),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class CartItem(Base):
    """Individual items in a shopping cart"""
    __tablename__ = "cart_items"
    
    id = Column(UUID, primary_key=True)
    cart_id = Column(UUID, ForeignKey("carts.id"), nullable=False, index=True)
    product_id = Column(String(255), nullable=False, index=True)
    store_id = Column(String(255), nullable=False, index=True)
    
    # Item details
    quantity = Column(Integer, nullable=False, default=1)
    unit_price = Column(Float, nullable=False)  # Price at time of add
    product_name = Column(String(500), nullable=True)  # Cache for quick display
    product_image_url = Column(String(500), nullable=True)
    
    # Metadata
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    
    # Validation flags
    is_price_valid = Column(Boolean, default=True)  # Price hasn't changed
    is_in_stock = Column(Boolean, default=True)  # Stock available
    validation_errors = Column(JSON, nullable=True)  # Errors during validation
    
    # Relationship
    cart = relationship("Cart", back_populates="items")
    
    def __repr__(self):
        return f"<CartItem(id={self.id}, product={self.product_id}, quantity={self.quantity}, store={self.store_id})>"
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "cart_id": str(self.cart_id),
            "product_id": self.product_id,
            "store_id": self.store_id,
            "quantity": self.quantity,
            "unit_price": self.unit_price,
            "total_price": self.unit_price * self.quantity,
            "product_name": self.product_name,
            "product_image_url": self.product_image_url,
            "is_price_valid": self.is_price_valid,
            "is_in_stock": self.is_in_stock,
            "validation_errors": self.validation_errors or [],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
