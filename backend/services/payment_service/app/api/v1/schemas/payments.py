"""Pydantic schemas for Payment Service"""
from pydantic import BaseModel, Field, field_validator, UUID4
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal
from enum import Enum


class PaymentMethodEnum(str, Enum):
    """Payment method enum"""
    UPI = "UPI"
    CARD = "CARD"
    WALLET = "WALLET"
    NET_BANKING = "NET_BANKING"
    COD = "COD"
    BNPL = "BNPL"


class PaymentStatusEnum(str, Enum):
    """Payment status enum"""
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    REFUND_PENDING = "REFUND_PENDING"
    REFUNDED = "REFUNDED"
    CANCELLED = "CANCELLED"


class PaymentGatewayEnum(str, Enum):
    """Payment gateway enum"""
    RAZORPAY = "RAZORPAY"
    CASHFREE = "CASHFREE"
    MANUAL = "MANUAL"


# Request Schemas
class PaymentInitiateRequest(BaseModel):
    """Request to initiate a payment"""
    order_id: UUID4 = Field(..., description="Order ID to pay for")
    customer_id: UUID4 = Field(..., description="Customer ID")
    amount: Decimal = Field(..., gt=0, description="Amount to pay")
    payment_method: PaymentMethodEnum = Field(..., description="Payment method")
    payment_gateway: PaymentGatewayEnum = Field(default=PaymentGatewayEnum.RAZORPAY, description="Payment gateway")
    
    # Optional customer details
    customer_email: Optional[str] = Field(None, max_length=255)
    customer_phone: Optional[str] = Field(None, max_length=20)
    description: Optional[str] = Field(None, description="Payment description")
    
    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Amount must be greater than 0')
        if v > 100000:  # Max 1 lakh for now
            raise ValueError('Amount exceeds maximum allowed')
        return v
    
    @field_validator('customer_phone')
    @classmethod
    def validate_phone(cls, v):
        if v and not v.replace('+', '').replace('-', '').replace(' ', '').isdigit():
            raise ValueError('Invalid phone number format')
        return v


class PaymentVerifyRequest(BaseModel):
    """Request to verify a payment (Razorpay)"""
    razorpay_order_id: str = Field(..., description="Razorpay order ID")
    razorpay_payment_id: str = Field(..., description="Razorpay payment ID")
    razorpay_signature: str = Field(..., description="Razorpay signature")


class RefundRequest(BaseModel):
    """Request to initiate refund"""
    payment_id: UUID4 = Field(..., description="Payment ID to refund")
    amount: Optional[Decimal] = Field(None, gt=0, description="Partial refund amount (None for full refund)")
    reason: str = Field(..., min_length=10, max_length=500, description="Refund reason")
    
    @field_validator('amount')
    @classmethod
    def validate_refund_amount(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Refund amount must be greater than 0')
        return v


# Response Schemas
class PaymentResponse(BaseModel):
    """Payment response"""
    id: UUID4
    order_id: UUID4
    customer_id: UUID4
    amount: Decimal
    currency: str
    payment_method: str
    payment_gateway: str
    status: str
    
    gateway_order_id: Optional[str] = None
    gateway_payment_id: Optional[str] = None
    gateway_response: Optional[Dict[str, Any]] = None
    
    description: Optional[str] = None
    customer_email: Optional[str] = None
    customer_phone: Optional[str] = None
    
    refund_amount: Optional[Decimal] = None
    refund_reason: Optional[str] = None
    
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class PaymentInitiateResponse(BaseModel):
    """Response after payment initiation"""
    payment_id: UUID4
    gateway_order_id: str
    payment_link: Optional[str] = None
    amount: Decimal
    currency: str
    status: str
    
    # Gateway-specific data
    razorpay_key_id: Optional[str] = None
    cashfree_session_id: Optional[str] = None


class PaymentLogResponse(BaseModel):
    """Payment log entry"""
    id: UUID4
    payment_id: UUID4
    event_type: str
    status_from: Optional[str]
    status_to: Optional[str]
    event_data: Optional[Dict[str, Any]]
    error_message: Optional[str]
    triggered_by: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class StandardResponse(BaseModel):
    """Standard API response wrapper"""
    success: bool
    message: str
    data: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None


# Webhook Schemas
class RazorpayWebhookPayload(BaseModel):
    """Razorpay webhook payload"""
    entity: str
    account_id: str
    event: str
    contains: List[str]
    payload: Dict[str, Any]
    created_at: int


class CashfreeWebhookPayload(BaseModel):
    """Cashfree webhook payload"""
    type: str
    data: Dict[str, Any]
