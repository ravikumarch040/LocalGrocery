"""Pydantic schemas for Order Service"""
from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal
from uuid import UUID
from app.models import OrderStatus, PaymentStatus


# ==================== Order Item Schemas ====================

class OrderItemBase(BaseModel):
    """Base order item schema"""
    product_id: UUID
    product_name: str = Field(..., min_length=1, max_length=255)
    quantity: int = Field(..., gt=0, le=1000)
    unit_price: Decimal = Field(..., gt=0, max_digits=10, decimal_places=2)
    variant_data: Optional[Dict[str, Any]] = Field(default_factory=dict)


class OrderItemCreate(OrderItemBase):
    """Create order item request"""
    pass


class OrderItemResponse(OrderItemBase):
    """Order item response"""
    id: UUID
    order_id: UUID
    total_price: Decimal
    status: OrderStatus
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ==================== Order Schemas ====================

class OrderBase(BaseModel):
    """Base order schema"""
    customer_id: UUID
    store_id: UUID
    payment_method: str = Field(..., min_length=1, max_length=50)
    delivery_address: Dict[str, Any] = Field(...)
    notes: Optional[str] = None
    
    @field_validator('delivery_address')
    @classmethod
    def validate_address(cls, v):
        required_fields = {'street', 'city', 'pincode'}
        if not isinstance(v, dict) or not required_fields.issubset(v.keys()):
            raise ValueError(f"Address must contain: {required_fields}")
        return v


class OrderCreate(OrderBase):
    """Create order request"""
    items: List[OrderItemCreate] = Field(..., min_items=1)
    
    @field_validator('items')
    @classmethod
    def validate_items(cls, v):
        if not v:
            raise ValueError('At least one item required')
        return v


class OrderUpdate(BaseModel):
    """Update order request"""
    status: Optional[OrderStatus] = None
    payment_status: Optional[PaymentStatus] = None
    notes: Optional[str] = None


class OrderResponse(OrderBase):
    """Order response"""
    id: UUID
    order_number: str
    status: OrderStatus
    payment_status: PaymentStatus
    subtotal: Decimal
    tax: Decimal
    delivery_fee: Decimal
    discount: Decimal
    total_amount: Decimal
    items: List[OrderItemResponse]
    created_at: datetime
    updated_at: datetime
    confirmed_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class OrderListResponse(BaseModel):
    """Order list response"""
    orders: List[OrderResponse]
    total: int
    page: int
    page_size: int


# ==================== Common Responses ====================

class StandardResponse(BaseModel):
    """Standard API response"""
    success: bool
    message: str
    data: Optional[Any] = None
