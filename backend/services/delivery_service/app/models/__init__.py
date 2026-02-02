"""Database models for Delivery Service"""
from sqlalchemy import Column, String, DateTime, Enum as SQLEnum, Text, Numeric, Float, Boolean, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from enum import Enum
from app.database import Base


class DeliveryStatus(str, Enum):
    """Delivery status enum"""
    PENDING = "PENDING"  # Waiting for assignment
    ASSIGNED = "ASSIGNED"  # Assigned to delivery partner
    PICKED_UP = "PICKED_UP"  # Delivery partner picked up from store
    IN_TRANSIT = "IN_TRANSIT"  # On the way to customer
    DELIVERED = "DELIVERED"  # Successfully delivered
    FAILED = "FAILED"  # Delivery failed
    CANCELLED = "CANCELLED"  # Delivery cancelled


class DeliveryPartnerStatus(str, Enum):
    """Delivery partner availability status"""
    AVAILABLE = "AVAILABLE"
    BUSY = "BUSY"
    OFFLINE = "OFFLINE"


class VehicleType(str, Enum):
    """Vehicle type enum"""
    BIKE = "BIKE"
    SCOOTER = "SCOOTER"
    BICYCLE = "BICYCLE"
    CAR = "CAR"


class Delivery(Base):
    """Delivery model"""
    __tablename__ = "deliveries"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), nullable=False, index=True, unique=True)
    
    # Delivery partner
    delivery_partner_id = Column(UUID(as_uuid=True), index=True)
    partner_name = Column(String(255))
    partner_phone = Column(String(20))
    
    # Status
    status = Column(SQLEnum(DeliveryStatus), default=DeliveryStatus.PENDING, nullable=False, index=True)
    
    # Locations (stored as JSONB with lat, lng, address)
    pickup_location = Column(JSONB, nullable=False)  # Store location
    delivery_location = Column(JSONB, nullable=False)  # Customer location
    current_location = Column(JSONB)  # Current delivery partner location
    
    # Distance & ETA
    distance_km = Column(Float)  # Distance in kilometers
    estimated_time_minutes = Column(Float)  # ETA in minutes
    actual_time_minutes = Column(Float)  # Actual delivery time
    
    # Delivery fee
    delivery_fee = Column(Numeric(10, 2))
    
    # Route optimization
    optimized_route = Column(JSONB)  # Waypoints for optimized route
    
    # Timestamps
    assigned_at = Column(DateTime(timezone=True))
    picked_up_at = Column(DateTime(timezone=True))
    in_transit_at = Column(DateTime(timezone=True))
    delivered_at = Column(DateTime(timezone=True))
    
    # Notes
    delivery_instructions = Column(Text)
    failure_reason = Column(Text)
    
    # Metadata
    custom_fields = Column(JSONB)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Indexes
    __table_args__ = (
        Index('ix_deliveries_partner_status', delivery_partner_id, status),
        Index('ix_deliveries_status_created', status, created_at),
    )


class DeliveryPartner(Base):
    """Delivery partner model"""
    __tablename__ = "delivery_partners"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Personal info
    name = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=False, unique=True, index=True)
    email = Column(String(255))
    
    # Vehicle
    vehicle_type = Column(SQLEnum(VehicleType), nullable=False)
    vehicle_number = Column(String(50))
    
    # Status
    status = Column(SQLEnum(DeliveryPartnerStatus), default=DeliveryPartnerStatus.OFFLINE, nullable=False, index=True)
    is_verified = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Location
    current_location = Column(JSONB)  # {lat, lng, updated_at}
    service_area = Column(JSONB)  # Geo-polygon or radius
    
    # Stats
    total_deliveries = Column(Numeric(10, 0), default=0)
    successful_deliveries = Column(Numeric(10, 0), default=0)
    rating = Column(Float, default=0.0)
    total_ratings = Column(Numeric(10, 0), default=0)
    
    # Documents
    documents = Column(JSONB)  # License, vehicle RC, etc.
    
    # Metadata
    custom_fields = Column(JSONB)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_active_at = Column(DateTime(timezone=True))
    
    # Indexes
    __table_args__ = (
        Index('ix_partners_status_location', status, current_location),
    )


class DeliveryTracking(Base):
    """Delivery tracking events for audit trail"""
    __tablename__ = "delivery_tracking"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    delivery_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Event details
    event_type = Column(String(50), nullable=False)  # ASSIGNED, PICKED_UP, LOCATION_UPDATE, etc.
    status_from = Column(String(50))
    status_to = Column(String(50))
    
    # Location at event time
    location = Column(JSONB)
    
    # Event data
    event_data = Column(JSONB)
    notes = Column(Text)
    
    # Source
    triggered_by = Column(String(50))  # SYSTEM, PARTNER, CUSTOMER, ADMIN
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    __table_args__ = (
        Index('ix_tracking_delivery_created', delivery_id, created_at),
    )
