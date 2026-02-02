from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class StockStatusEnum(str, Enum):
    IN_STOCK = "IN_STOCK"
    LOW_STOCK = "LOW_STOCK"
    OUT_OF_STOCK = "OUT_OF_STOCK"


class ReservationStatusEnum(str, Enum):
    RESERVED = "RESERVED"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"


class InventoryLogEnum(str, Enum):
    STOCK_ADDED = "STOCK_ADDED"
    STOCK_REMOVED = "STOCK_REMOVED"
    STOCK_ADJUSTED = "STOCK_ADJUSTED"
    STOCK_RESERVED = "STOCK_RESERVED"
    STOCK_UNRESERVED = "STOCK_UNRESERVED"
    STOCK_CONFIRMED = "STOCK_CONFIRMED"
    LOW_STOCK_ALERT = "LOW_STOCK_ALERT"
    OUT_OF_STOCK_ALERT = "OUT_OF_STOCK_ALERT"


# ========== Inventory Requests ==========

class CreateInventoryRequest(BaseModel):
    store_id: str = Field(..., min_length=1)
    product_id: str = Field(..., min_length=1)
    stock_qty: int = Field(..., ge=0)
    cost_price: float = Field(..., gt=0)
    selling_price: float = Field(..., gt=0)
    reorder_level: int = Field(default=10, ge=1)
    reorder_qty: int = Field(default=50, ge=1)
    supplier_id: Optional[str] = None
    batch_number: Optional[str] = None
    expiry_date: Optional[datetime] = None
    product_metadata: Optional[Dict[str, Any]] = None
    
    @field_validator('reorder_qty')
    @classmethod
    def validate_reorder_qty(cls, v, info):
        if 'reorder_level' in info.data and v < info.data['reorder_level']:
            raise ValueError('reorder_qty must be >= reorder_level')
        return v


class UpdateInventoryRequest(BaseModel):
    stock_qty: Optional[int] = Field(None, ge=0)
    cost_price: Optional[float] = Field(None, gt=0)
    selling_price: Optional[float] = Field(None, gt=0)
    reorder_level: Optional[int] = Field(None, ge=1)
    reorder_qty: Optional[int] = Field(None, ge=1)
    expiry_date: Optional[datetime] = None
    product_metadata: Optional[Dict[str, Any]] = None


class AdjustStockRequest(BaseModel):
    qty_change: int = Field(..., description="Positive = add, Negative = remove")
    source: str = Field(..., description="MANUAL_ADJUSTMENT, RETURN, DAMAGE, etc.")
    user_id: Optional[str] = None
    notes: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class ReserveInventoryRequest(BaseModel):
    order_id: str = Field(..., min_length=1)
    customer_id: str = Field(..., min_length=1)
    items: List[Dict[str, Any]] = Field(...)  # [{store_id, product_id, qty}]
    
    @field_validator('items')
    @classmethod
    def validate_items(cls, v):
        if not v or len(v) == 0:
            raise ValueError('At least one item required')
        for item in v:
            if not all(k in item for k in ['store_id', 'product_id', 'qty']):
                raise ValueError('Each item must have store_id, product_id, qty')
            if item['qty'] <= 0:
                raise ValueError('Item quantity must be > 0')
        return v


class ConfirmReservationRequest(BaseModel):
    reason: Optional[str] = None


class CancelReservationRequest(BaseModel):
    reason: Optional[str] = None


class CheckAvailabilityRequest(BaseModel):
    items: List[Dict[str, Any]] = Field(...)  # [{store_id, product_id, qty}]


# ========== Inventory Responses ==========

class InventoryResponse(BaseModel):
    id: str
    store_id: str
    product_id: str
    stock_qty: int
    reserved_qty: int
    available_qty: int
    cost_price: float
    selling_price: float
    status: StockStatusEnum
    reorder_level: int
    reorder_qty: int
    supplier_id: Optional[str] = None
    batch_number: Optional[str] = None
    expiry_date: Optional[datetime] = None
    product_metadata: Optional[Dict[str, Any]] = None
    last_stock_check: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ReservationItemResponse(BaseModel):
    store_id: str
    product_id: str
    qty: int
    inventory_id: Optional[str] = None


class ReservationResponse(BaseModel):
    id: str
    order_id: str
    customer_id: str
    items: List[ReservationItemResponse]
    status: ReservationStatusEnum
    reserved_at: datetime
    confirmed_at: Optional[datetime] = None
    expires_at: datetime
    cancelled_at: Optional[datetime] = None
    reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class AvailabilityCheckResponse(BaseModel):
    available: bool
    items_status: List[Dict[str, Any]]  # [{product_id, requested_qty, available_qty, in_stock}]
    unavailable_items: List[str] = []  # product IDs that are out of stock


class StockAuditLogResponse(BaseModel):
    id: str
    inventory_id: str
    event_type: InventoryLogEnum
    old_qty: int
    new_qty: int
    qty_changed: int
    order_id: Optional[str] = None
    user_id: Optional[str] = None
    source: str
    notes: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class StandardResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None
