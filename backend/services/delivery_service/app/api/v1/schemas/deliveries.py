"""Pydantic schemas for Delivery Service"""
from pydantic import BaseModel, Field, field_validator, UUID4
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal
from enum import Enum


class DeliveryStatusEnum(str, Enum):
    """Delivery status enum"""
    PENDING = "PENDING"
    ASSIGNED = "ASSIGNED"
    PICKED_UP = "PICKED_UP"
    IN_TRANSIT = "IN_TRANSIT"
    DELIVERED = "DELIVERED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class PartnerStatusEnum(str, Enum):
    """Delivery partner status enum"""
    AVAILABLE = "AVAILABLE"
    BUSY = "BUSY"
    OFFLINE = "OFFLINE"


class VehicleTypeEnum(str, Enum):
    """Vehicle type enum"""
    BIKE = "BIKE"
    SCOOTER = "SCOOTER"
    BICYCLE = "BICYCLE"
    CAR = "CAR"


class LocationSchema(BaseModel):
    """Location coordinates"""
    lat: float = Field(..., ge=-90, le=90, description="Latitude")
    lng: float = Field(..., ge=-180, le=180, description="Longitude")
    address: Optional[str] = None


# Request Schemas
class DeliveryCreateRequest(BaseModel):
    """Request to create a delivery"""
    order_id: UUID4 = Field(..., description="Order ID")
    pickup_location: LocationSchema = Field(..., description="Store location")
    delivery_location: LocationSchema = Field(..., description="Customer location")
    delivery_instructions: Optional[str] = Field(None, max_length=500)


class AssignDeliveryRequest(BaseModel):
    """Request to assign delivery to partner"""
    delivery_id: UUID4
    delivery_partner_id: UUID4


class UpdateDeliveryStatusRequest(BaseModel):
    """Request to update delivery status"""
    status: DeliveryStatusEnum
    location: Optional[LocationSchema] = None
    notes: Optional[str] = None


class UpdatePartnerLocationRequest(BaseModel):
    """Request to update delivery partner location"""
    location: LocationSchema


class PartnerStatusUpdateRequest(BaseModel):
    """Request to update partner status"""
    status: PartnerStatusEnum


# Alias for consistency with endpoint
UpdatePartnerStatusRequest = PartnerStatusUpdateRequest


# Response Schemas
class DeliveryResponse(BaseModel):
    """Delivery response"""
    id: UUID4
    order_id: UUID4
    delivery_partner_id: Optional[UUID4]
    partner_name: Optional[str]
    partner_phone: Optional[str]
    status: str
    pickup_location: Dict[str, Any]
    delivery_location: Dict[str, Any]
    current_location: Optional[Dict[str, Any]]
    distance_km: Optional[float]
    estimated_time_minutes: Optional[float]
    actual_time_minutes: Optional[float]
    delivery_fee: Optional[Decimal]
    assigned_at: Optional[datetime]
    picked_up_at: Optional[datetime]
    in_transit_at: Optional[datetime]
    delivered_at: Optional[datetime]
    delivery_instructions: Optional[str]
    failure_reason: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class DeliveryPartnerResponse(BaseModel):
    """Delivery partner response"""
    id: UUID4
    name: str
    phone: str
    email: Optional[str]
    vehicle_type: str
    vehicle_number: Optional[str]
    status: str
    is_verified: bool
    is_active: bool
    current_location: Optional[Dict[str, Any]]
    total_deliveries: int
    successful_deliveries: int
    rating: float
    created_at: datetime
    last_active_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class DeliveryTrackingResponse(BaseModel):
    """Delivery tracking event"""
    id: UUID4
    delivery_id: UUID4
    event_type: str
    status_from: Optional[str]
    status_to: Optional[str]
    location: Optional[Dict[str, Any]]
    event_data: Optional[Dict[str, Any]]
    notes: Optional[str]
    triggered_by: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class DeliveryAssignmentResponse(BaseModel):
    """Response after delivery assignment"""
    delivery_id: UUID4
    delivery_partner_id: UUID4
    partner_name: str
    estimated_time_minutes: float
    distance_km: float


class StandardResponse(BaseModel):
    """Standard API response wrapper"""
    success: bool
    message: str
    data: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None


class NearbyPartnersResponse(BaseModel):
    """Nearby available partners"""
    partners: List[DeliveryPartnerResponse]
    count: int
