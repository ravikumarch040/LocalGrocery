"""Database models for Notification Service"""
from sqlalchemy import Column, String, Boolean, Integer, DateTime, Text, Index, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.database import Base
from datetime import datetime, UTC
import uuid
import enum


class NotificationType(str, enum.Enum):
    """Notification type enum"""
    SMS = "SMS"
    PUSH = "PUSH"
    EMAIL = "EMAIL"


class NotificationStatus(str, enum.Enum):
    """Notification status enum"""
    PENDING = "PENDING"
    SENT = "SENT"
    DELIVERED = "DELIVERED"
    FAILED = "FAILED"
    RETRY = "RETRY"


class NotificationPriority(str, enum.Enum):
    """Notification priority enum"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"


class Notification(Base):
    """Notification model for tracking all notifications"""
    __tablename__ = "notifications"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Recipient information
    user_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    recipient_phone = Column(String(20), nullable=True)
    recipient_email = Column(String(255), nullable=True)
    fcm_token = Column(String(255), nullable=True)
    
    # Notification details
    type = Column(SQLEnum(NotificationType), nullable=False, index=True)
    status = Column(SQLEnum(NotificationStatus), nullable=False, default=NotificationStatus.PENDING, index=True)
    priority = Column(SQLEnum(NotificationPriority), nullable=False, default=NotificationPriority.MEDIUM)
    
    # Content
    template_id = Column(String(100), nullable=True)
    subject = Column(String(255), nullable=True)  # For email/push title
    message = Column(Text, nullable=False)
    data = Column(JSONB, nullable=True)  # Additional data (deep link, action buttons, etc.)
    
    # Delivery tracking
    sent_at = Column(DateTime(timezone=True), nullable=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    failed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Error handling
    retry_count = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    
    # Provider response
    provider_response = Column(JSONB, nullable=True)
    provider_message_id = Column(String(255), nullable=True)
    
    # Metadata
    reference_type = Column(String(50), nullable=True, index=True)  # ORDER, PAYMENT, DELIVERY, AUTH
    reference_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    custom_fields = Column(JSONB, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))
    
    # Indexes
    __table_args__ = (
        Index('ix_notifications_status_created', 'status', 'created_at'),
        Index('ix_notifications_type_status', 'type', 'status'),
        Index('ix_notifications_reference', 'reference_type', 'reference_id'),
        Index('ix_notifications_user_created', 'user_id', 'created_at'),
    )


class DeviceToken(Base):
    """FCM device tokens for push notifications"""
    __tablename__ = "device_tokens"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # User and device info
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    device_type = Column(String(20), nullable=False)  # IOS, ANDROID, WEB
    fcm_token = Column(String(255), nullable=False, unique=True, index=True)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    
    # Device metadata
    device_info = Column(JSONB, nullable=True)  # OS version, app version, etc.
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))


class NotificationTemplate(Base):
    """Pre-defined notification templates"""
    __tablename__ = "notification_templates"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Template identification
    template_key = Column(String(100), nullable=False, unique=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Template content
    type = Column(SQLEnum(NotificationType), nullable=False)
    subject_template = Column(String(255), nullable=True)  # For email/push title
    message_template = Column(Text, nullable=False)
    
    # Configuration
    is_active = Column(Boolean, default=True, nullable=False)
    priority = Column(SQLEnum(NotificationPriority), nullable=False, default=NotificationPriority.MEDIUM)
    
    # Metadata
    variables = Column(JSONB, nullable=True)  # List of required variables
    custom_fields = Column(JSONB, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))


class NotificationPreference(Base):
    """User notification preferences"""
    __tablename__ = "notification_preferences"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # User
    user_id = Column(UUID(as_uuid=True), nullable=False, unique=True, index=True)
    
    # Preferences by category
    order_updates_sms = Column(Boolean, default=True, nullable=False)
    order_updates_push = Column(Boolean, default=True, nullable=False)
    order_updates_email = Column(Boolean, default=True, nullable=False)
    
    payment_updates_sms = Column(Boolean, default=True, nullable=False)
    payment_updates_push = Column(Boolean, default=True, nullable=False)
    payment_updates_email = Column(Boolean, default=False, nullable=False)
    
    delivery_updates_sms = Column(Boolean, default=True, nullable=False)
    delivery_updates_push = Column(Boolean, default=True, nullable=False)
    delivery_updates_email = Column(Boolean, default=False, nullable=False)
    
    promotional_sms = Column(Boolean, default=False, nullable=False)
    promotional_push = Column(Boolean, default=True, nullable=False)
    promotional_email = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))
