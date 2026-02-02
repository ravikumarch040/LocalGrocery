from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime


# ==================== Cart Item Schemas ====================

class CartItemCreate(BaseModel):
    """Schema for adding item to cart"""
    product_id: str = Field(..., min_length=1, description="Product ID")
    store_id: str = Field(..., min_length=1, description="Store ID")
    quantity: int = Field(..., gt=0, le=1000, description="Quantity (1-1000)")
    unit_price: float = Field(..., gt=0, description="Current product price")
    product_name: Optional[str] = None
    product_image_url: Optional[str] = None


class CartItemUpdate(BaseModel):
    """Schema for updating cart item quantity"""
    quantity: int = Field(..., gt=0, le=1000, description="New quantity")


class CartItemResponse(BaseModel):
    """Schema for cart item response"""
    id: str
    cart_id: str
    product_id: str
    store_id: str
    quantity: int
    unit_price: float
    product_name: Optional[str] = None
    product_image_url: Optional[str] = None
    is_price_valid: bool
    is_in_stock: bool
    validation_errors: Optional[List[str]] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ==================== Cart Schemas ====================

class CartCreate(BaseModel):
    """Schema for creating a cart"""
    customer_id: str = Field(..., min_length=1, description="Customer ID")


class CartResponse(BaseModel):
    """Schema for cart response"""
    id: str
    customer_id: str
    items_count: int
    total_items: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CartDetailedResponse(BaseModel):
    """Detailed cart response with all items"""
    id: str
    customer_id: str
    items: List[CartItemResponse]
    items_count: int
    total_items: int
    total_amount: float
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ==================== Validation Schemas ====================

class CartValidationResult(BaseModel):
    """Result of cart validation"""
    cart_id: str
    is_valid: bool
    invalid_items: List[dict]
    errors: List[str] = []
    message: str


class CartItemValidationError(BaseModel):
    """Validation error for an item"""
    item_id: str
    product_id: str
    errors: List[str]


# ==================== Checkout Schemas ====================

class CheckoutRequest(BaseModel):
    """Request to initiate checkout from cart"""
    cart_id: str = Field(..., description="Cart ID")
    customer_id: str = Field(..., description="Customer ID")
    address_id: Optional[str] = None
    payment_method: Optional[str] = None


class CheckoutResponse(BaseModel):
    """Response after checkout"""
    success: bool
    message: str
    order_ids: Optional[List[str]] = None
    split_orders: Optional[int] = None  # Number of orders (one per store)
    orders_count: Optional[int] = None
    error: Optional[str] = None


# ==================== Batch Update Schemas ====================

class BulkAddItem(BaseModel):
    """Item in bulk add request"""
    product_id: str
    store_id: str
    quantity: int
    unit_price: float
    product_name: Optional[str] = None
    product_image_url: Optional[str] = None


class BulkAddRequest(BaseModel):
    """Request to add multiple items at once"""
    cart_id: Optional[str] = None
    items: List[BulkAddItem] = Field(..., min_items=1)
    
    @field_validator('items')
    @classmethod
    def validate_items_not_empty(cls, v):
        if not v:
            raise ValueError('At least one item required')
        return v


class BulkAddResponse(BaseModel):
    """Response after bulk add"""
    cart_id: str
    added_count: int
    failed_count: int
    errors: Optional[List[dict]] = None


# ==================== Error Schemas ====================

class ErrorResponse(BaseModel):
    """Standard error response"""
    success: bool = False
    message: str
    error_code: Optional[str] = None
    details: Optional[dict] = None


class CartNotFoundError(ErrorResponse):
    """Cart not found error"""
    message: str = "Cart not found"
    error_code: str = "CART_NOT_FOUND"


class InvalidQuantityError(ErrorResponse):
    """Invalid quantity error"""
    message: str = "Invalid quantity"
    error_code: str = "INVALID_QUANTITY"


class CartFullError(ErrorResponse):
    """Cart is full error"""
    message: str = "Cart has reached maximum items"
    error_code: str = "CART_FULL"
