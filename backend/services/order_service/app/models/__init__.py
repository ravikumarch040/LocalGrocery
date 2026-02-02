"""Database models for Order Service"""
from sqlalchemy import Column, String, Boolean, DateTime, Integer, Enum as SQLEnum, Text, Numeric, ForeignKey, Index, Sequence
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, RelationshipProperty
import uuid
from enum import Enum
from app.database import Base


class OrderStatus(str, Enum):
    """Order status enum"""
    PLACED = "PLACED"
    CONFIRMED = "CONFIRMED"
    PACKED = "PACKED"
    OUT_FOR_DELIVERY = "OUT_FOR_DELIVERY"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"


class PaymentStatus(str, Enum):
    """Payment status enum"""
    PENDING = "PENDING"
    PAID = "PAID"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"


class Order(Base):
    """Order model (main order record)"""
    __tablename__ = "orders"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    store_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Order details
    order_number = Column(String(50), unique=True, nullable=False, index=True)
    status = Column(SQLEnum(OrderStatus), default=OrderStatus.PLACED, nullable=False, index=True)
    payment_status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)
    
    # Pricing
    subtotal = Column(Numeric(10, 2), nullable=False)  # Sum of all items (qty * price)
    tax = Column(Numeric(10, 2), default=0)
    delivery_fee = Column(Numeric(10, 2), default=0)
    discount = Column(Numeric(10, 2), default=0)
    total_amount = Column(Numeric(10, 2), nullable=False)
    
    # Delivery address
    delivery_address = Column(JSONB)  # {street, city, pincode, lat, lng, phone}
    
    # Payment info
    payment_method = Column(String(50))  # UPI, Card, Wallet, etc.
    payment_gateway = Column(String(50))  # razorpay, cashfree
    payment_gateway_order_id = Column(String(255))
    idempotency_key = Column(String(255), unique=True, index=True)
    
    # Additional metadata
    notes = Column(Text)
    custom_fields = Column(JSONB, default=dict)  # Custom fields
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    confirmed_at = Column(DateTime(timezone=True), nullable=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan", lazy="selectin")
    
    # Indexes
    __table_args__ = (
        Index('ix_orders_customer_created', customer_id, created_at),
        Index('ix_orders_store_status', store_id, status),
        Index('ix_orders_payment_status', payment_status),
    )


class OrderItem(Base):
    """Order item model (line items in order)"""
    __tablename__ = "order_items"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey('orders.id'), nullable=False, index=True)
    product_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Item details
    product_name = Column(String(255), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    total_price = Column(Numeric(10, 2), nullable=False)  # qty * unit_price
    
    # Product variant info (if applicable)
    variant_data = Column(JSONB, default=dict)  # {name, sku, attributes}
    
    # Status tracking
    status = Column(SQLEnum(OrderStatus), default=OrderStatus.PLACED, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    order = relationship("Order", back_populates="items")
    
    __table_args__ = (
        Index('ix_order_items_product', product_id),
    )
