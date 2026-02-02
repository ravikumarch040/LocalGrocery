"""Pydantic schemas for Notification Service"""
from pydantic import BaseModel, Field, UUID4
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class NotificationTypeEnum(str, Enum):
    """Notification type"""
    SMS = "SMS"
    PUSH = "PUSH"
    EMAIL = "EMAIL"


class NotificationStatusEnum(str, Enum):
    """Notification status"""
    PENDING = "PENDING"
    SENT = "SENT"
    DELIVERED = "DELIVERED"
    FAILED = "FAILED"
    RETRY = "RETRY"


class NotificationPriorityEnum(str, Enum):
    """Notification priority"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"


class DeviceTypeEnum(str, Enum):
    """Device type"""
    IOS = "IOS"
    ANDROID = "ANDROID"
    WEB = "WEB"


# Request Schemas
class SendSMSRequest(BaseModel):
    """Request to send SMS"""
    phone: str = Field(..., description="Phone number with country code", pattern=r"^\+?[1-9]\d{1,14}$")
    message: str = Field(..., min_length=1, max_length=1000)
    template_id: Optional[str] = None
    reference_type: Optional[str] = None
    reference_id: Optional[UUID4] = None
    priority: NotificationPriorityEnum = NotificationPriorityEnum.MEDIUM


class SendPushRequest(BaseModel):
    """Request to send push notification"""
    user_id: Optional[UUID4] = None
    fcm_token: Optional[str] = None
    title: str = Field(..., min_length=1, max_length=255)
    body: str = Field(..., min_length=1, max_length=1000)
    data: Optional[Dict[str, Any]] = None
    priority: NotificationPriorityEnum = NotificationPriorityEnum.MEDIUM
    reference_type: Optional[str] = None
    reference_id: Optional[UUID4] = None


class SendEmailRequest(BaseModel):
    """Request to send email"""
    email: str = Field(..., description="Email address")
    subject: str = Field(..., min_length=1, max_length=255)
    body: str = Field(..., min_length=1)
    html: Optional[str] = None
    template_id: Optional[str] = None
    reference_type: Optional[str] = None
    reference_id: Optional[UUID4] = None


class BulkNotificationRequest(BaseModel):
    """Request to send bulk notifications"""
    type: NotificationTypeEnum
    recipients: List[str] = Field(..., min_items=1, max_items=1000)
    message: str = Field(..., min_length=1)
    subject: Optional[str] = None
    template_id: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    priority: NotificationPriorityEnum = NotificationPriorityEnum.LOW


class RegisterDeviceTokenRequest(BaseModel):
    """Request to register FCM device token"""
    user_id: UUID4
    fcm_token: str = Field(..., min_length=1)
    device_type: DeviceTypeEnum
    device_info: Optional[Dict[str, Any]] = None


class UpdatePreferencesRequest(BaseModel):
    """Request to update notification preferences"""
    order_updates_sms: Optional[bool] = None
    order_updates_push: Optional[bool] = None
    order_updates_email: Optional[bool] = None
    payment_updates_sms: Optional[bool] = None
    payment_updates_push: Optional[bool] = None
    payment_updates_email: Optional[bool] = None
    delivery_updates_sms: Optional[bool] = None
    delivery_updates_push: Optional[bool] = None
    delivery_updates_email: Optional[bool] = None
    promotional_sms: Optional[bool] = None
    promotional_push: Optional[bool] = None
    promotional_email: Optional[bool] = None


class TemplateCreateRequest(BaseModel):
    """Request to create notification template"""
    template_key: str = Field(..., pattern=r'^[a-z0-9_]+$')
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    type: NotificationTypeEnum
    subject_template: Optional[str] = None
    message_template: str = Field(..., min_length=1)
    priority: NotificationPriorityEnum = NotificationPriorityEnum.MEDIUM
    variables: Optional[List[str]] = None


# Response Schemas
class NotificationResponse(BaseModel):
    """Notification response"""
    id: UUID4
    user_id: Optional[UUID4]
    type: str
    status: str
    priority: str
    subject: Optional[str]
    message: str
    data: Optional[Dict[str, Any]]
    sent_at: Optional[datetime]
    delivered_at: Optional[datetime]
    failed_at: Optional[datetime]
    retry_count: int
    error_message: Optional[str]
    provider_message_id: Optional[str]
    reference_type: Optional[str]
    reference_id: Optional[UUID4]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class DeviceTokenResponse(BaseModel):
    """Device token response"""
    id: UUID4
    user_id: UUID4
    device_type: str
    fcm_token: str
    is_active: bool
    last_used_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class NotificationTemplateResponse(BaseModel):
    """Template response"""
    id: UUID4
    template_key: str
    name: str
    description: Optional[str]
    type: str
    subject_template: Optional[str]
    message_template: str
    is_active: bool
    priority: str
    variables: Optional[Dict[str, Any]]
    created_at: datetime
    
    class Config:
        from_attributes = True


class NotificationPreferenceResponse(BaseModel):
    """Preference response"""
    id: UUID4
    user_id: UUID4
    order_updates_sms: bool
    order_updates_push: bool
    order_updates_email: bool
    payment_updates_sms: bool
    payment_updates_push: bool
    payment_updates_email: bool
    delivery_updates_sms: bool
    delivery_updates_push: bool
    delivery_updates_email: bool
    promotional_sms: bool
    promotional_push: bool
    promotional_email: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class SendResponse(BaseModel):
    """Response after sending notification"""
    success: bool
    notification_id: Optional[UUID4] = None
    message: str
    provider_message_id: Optional[str] = None


class BulkSendResponse(BaseModel):
    """Response after bulk send"""
    success: bool
    total: int
    sent: int
    failed: int
    notification_ids: List[UUID4]
