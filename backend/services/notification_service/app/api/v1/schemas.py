"""Pydantic schemas for Notification Service"""
from pydantic import BaseModel, Field, UUID4
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class NotificationTypeEnum(str, Enum):
    """Notification type"""
    OTP = "OTP"
    ORDER_STATUS = "ORDER_STATUS"
    PAYMENT_CONFIRMATION = "PAYMENT_CONFIRMATION"
    DELIVERY_UPDATE = "DELIVERY_UPDATE"
    PROMO = "PROMO"
    GENERAL = "GENERAL"


class NotificationChannelEnum(str, Enum):
    """Notification channel"""
    SMS = "SMS"
    PUSH = "PUSH"
    EMAIL = "EMAIL"


class NotificationStatusEnum(str, Enum):
    """Notification status"""
    PENDING = "PENDING"
    SENT = "SENT"
    DELIVERED = "DELIVERED"
    FAILED = "FAILED"


# Request Schemas
class SendOTPRequest(BaseModel):
    """Send OTP request"""
    user_id: UUID4
    phone: str = Field(..., min_length=10, max_length=15)
    purpose: str = Field(default="login")  # login, password_reset, verification


class VerifyOTPRequest(BaseModel):
    """Verify OTP request"""
    phone: str
    otp: str = Field(..., min_length=6, max_length=6)


class SendNotificationRequest(BaseModel):
    """Send notification request"""
    user_id: UUID4
    notification_type: NotificationTypeEnum
    channel: NotificationChannelEnum
    title: Optional[str] = None
    message: str
    recipient_address: Optional[str] = None  # Phone, email, or FCM token
    data: Optional[Dict[str, Any]] = None


class SendBulkNotificationRequest(BaseModel):
    """Send bulk notifications"""
    notification_type: NotificationTypeEnum
    channel: NotificationChannelEnum
    title: Optional[str] = None
    message: str
    user_ids: list[UUID4] = Field(..., min_items=1, max_items=1000)
    data: Optional[Dict[str, Any]] = None


class CreateTemplateRequest(BaseModel):
    """Create notification template"""
    name: str = Field(..., min_length=1, max_length=100)
    notification_type: NotificationTypeEnum
    channel: NotificationChannelEnum
    title: Optional[str] = None
    message: str
    is_active: bool = True


# Response Schemas
class NotificationResponse(BaseModel):
    """Notification response"""
    id: UUID4
    user_id: UUID4
    notification_type: str
    channel: str
    status: str
    title: Optional[str]
    message: str
    recipient_address: str
    sent_at: Optional[datetime]
    delivered_at: Optional[datetime]
    is_read: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class TemplateResponse(BaseModel):
    """Template response"""
    id: UUID4
    name: str
    notification_type: str
    channel: str
    title: Optional[str]
    message: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class OTPResponse(BaseModel):
    """OTP response"""
    phone: str
    message: str
    sent_at: datetime
    expires_at: datetime


class StandardResponse(BaseModel):
    """Standard API response"""
    success: bool
    message: str
    data: Optional[Any] = None
