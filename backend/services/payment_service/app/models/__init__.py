"""Database models for Payment Service"""
from sqlalchemy import Column, String, DateTime, Enum as SQLEnum, Text, Numeric, ForeignKey, Index, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from enum import Enum
from app.database import Base


class PaymentMethod(str, Enum):
    """Payment method enum"""
    UPI = "UPI"
    CARD = "CARD"
    WALLET = "WALLET"
    NET_BANKING = "NET_BANKING"
    COD = "COD"
    BNPL = "BNPL"  # Buy Now Pay Later


class PaymentStatus(str, Enum):
    """Payment status enum"""
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    REFUND_PENDING = "REFUND_PENDING"
    REFUNDED = "REFUNDED"
    CANCELLED = "CANCELLED"


class PaymentGateway(str, Enum):
    """Payment gateway enum"""
    RAZORPAY = "RAZORPAY"
    CASHFREE = "CASHFREE"
    MANUAL = "MANUAL"  # For COD


class Payment(Base):
    """Payment transaction model"""
    __tablename__ = "payments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), nullable=False, index=True, unique=True)
    customer_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Payment details
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default="INR", nullable=False)
    payment_method = Column(SQLEnum(PaymentMethod), nullable=False)
    payment_gateway = Column(SQLEnum(PaymentGateway), nullable=False)
    status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False, index=True)
    
    # Gateway response
    gateway_order_id = Column(String(255), index=True)
    gateway_payment_id = Column(String(255), index=True)
    gateway_signature = Column(String(512))
    gateway_response = Column(JSONB)  # Full gateway response
    
    # Metadata
    description = Column(Text)
    customer_email = Column(String(255))
    customer_phone = Column(String(20))
    
    # Refund details
    refund_amount = Column(Numeric(10, 2), default=0)
    refund_reason = Column(Text)
    refund_initiated_at = Column(DateTime(timezone=True))
    refund_completed_at = Column(DateTime(timezone=True))
    
    # Idempotency
    idempotency_key = Column(String(255), unique=True, index=True)
    
    # Webhooks
    webhook_attempts = Column(JSONB, default=list)
    webhook_verified = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True))
    
    # Indexes
    __table_args__ = (
        Index('ix_payments_customer_status', customer_id, status),
        Index('ix_payments_gateway_order', payment_gateway, gateway_order_id),
        Index('ix_payments_created', created_at),
    )


class PaymentLog(Base):
    """Payment activity log for audit trail"""
    __tablename__ = "payment_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    payment_id = Column(UUID(as_uuid=True), ForeignKey('payments.id'), nullable=False, index=True)
    
    # Log details
    event_type = Column(String(50), nullable=False)  # CREATED, PROCESSING, SUCCESS, FAILED, REFUND, etc.
    status_from = Column(String(50))
    status_to = Column(String(50))
    
    # Event data
    event_data = Column(JSONB)
    error_message = Column(Text)
    
    # Source
    triggered_by = Column(String(50))  # USER, WEBHOOK, CRON, ADMIN
    ip_address = Column(String(45))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    __table_args__ = (
        Index('ix_payment_logs_payment_created', payment_id, created_at),
    )
