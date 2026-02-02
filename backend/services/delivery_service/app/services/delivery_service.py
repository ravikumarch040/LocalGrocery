"""Delivery Service - Business logic"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from app.models import Delivery, DeliveryPartner, DeliveryTracking, DeliveryStatus, DeliveryPartnerStatus
from app.api.v1.schemas.deliveries import DeliveryCreateRequest, UpdateDeliveryStatusRequest, LocationSchema
from app.config import settings
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, UTC
from geopy.distance import geodesic
import uuid
import httpx
import logging
import math

logger = logging.getLogger(__name__)


class DeliveryService:
    """Service for delivery operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_delivery(self, request: DeliveryCreateRequest) -> Delivery:
        """Create a new delivery"""
        # Calculate distance and ETA
        distance_km = self._calculate_distance(
            request.pickup_location.model_dump(),
            request.delivery_location.model_dump()
        )
        
        # Calculate delivery fee
        delivery_fee = self._calculate_delivery_fee(distance_km)
        
        # Calculate ETA
        estimated_time_minutes = self._calculate_eta(distance_km)
        
        # Create delivery
        delivery = Delivery(
            id=uuid.uuid4(),
            order_id=request.order_id,
            pickup_location=request.pickup_location.model_dump(),
            delivery_location=request.delivery_location.model_dump(),
            distance_km=distance_km,
            estimated_time_minutes=estimated_time_minutes,
            delivery_fee=delivery_fee,
            delivery_instructions=request.delivery_instructions,
            status=DeliveryStatus.PENDING,
        )
        
        self.db.add(delivery)
        await self.db.flush()
        
        # Log creation
        await self._log_tracking_event(
            delivery.id,
            "DELIVERY_CREATED",
            None,
            DeliveryStatus.PENDING.value,
            request.pickup_location.model_dump()
        )
        
        return delivery
    
    async def assign_delivery_partner(
        self,
        delivery_id: uuid.UUID,
        partner_id: Optional[uuid.UUID] = None
    ) -> Delivery:
        """Assign delivery to a partner (auto or manual)"""
        delivery = await self.get_delivery(delivery_id)
        if not delivery:
            raise ValueError(f"Delivery {delivery_id} not found")
        
        if delivery.status != DeliveryStatus.PENDING:
            raise ValueError(f"Cannot assign delivery with status {delivery.status}")
        
        # Auto-assign if partner not specified
        if not partner_id:
            partner = await self._find_nearest_available_partner(
                delivery.pickup_location
            )
            if not partner:
                raise ValueError("No available delivery partners found")
            partner_id = partner.id
        else:
            partner = await self.get_delivery_partner(partner_id)
            if not partner:
                raise ValueError(f"Partner {partner_id} not found")
            if partner.status != DeliveryPartnerStatus.AVAILABLE:
                raise ValueError(f"Partner is not available (status: {partner.status})")
        
        # Update delivery
        old_status = delivery.status
        delivery.delivery_partner_id = partner_id
        delivery.partner_name = partner.name
        delivery.partner_phone = partner.phone
        delivery.status = DeliveryStatus.ASSIGNED
        delivery.assigned_at = datetime.now(UTC)
        
        # Update partner status
        partner.status = DeliveryPartnerStatus.BUSY
        
        await self.db.flush()
        
        # Log assignment
        await self._log_tracking_event(
            delivery.id,
            "DELIVERY_ASSIGNED",
            old_status.value,
            DeliveryStatus.ASSIGNED.value,
            partner.current_location,
            {"partner_id": str(partner_id), "partner_name": partner.name}
        )
        
        # Notify Order Service
        await self._update_order_delivery_status(delivery.order_id, "ASSIGNED")
        
        return delivery
    
    async def update_delivery_status(
        self,
        delivery_id: uuid.UUID,
        status_request: UpdateDeliveryStatusRequest,
        partner_id: Optional[uuid.UUID] = None
    ) -> Delivery:
        """Update delivery status"""
        delivery = await self.get_delivery(delivery_id)
        if not delivery:
            raise ValueError(f"Delivery {delivery_id} not found")
        
        # Verify partner if provided
        if partner_id and delivery.delivery_partner_id != partner_id:
            raise ValueError("Partner not authorized for this delivery")
        
        old_status = delivery.status
        new_status = DeliveryStatus(status_request.status.value)
        
        # Validate status transition
        valid_transitions = {
            DeliveryStatus.PENDING: [DeliveryStatus.ASSIGNED, DeliveryStatus.CANCELLED],
            DeliveryStatus.ASSIGNED: [DeliveryStatus.PICKED_UP, DeliveryStatus.CANCELLED],
            DeliveryStatus.PICKED_UP: [DeliveryStatus.IN_TRANSIT, DeliveryStatus.FAILED],
            DeliveryStatus.IN_TRANSIT: [DeliveryStatus.DELIVERED, DeliveryStatus.FAILED],
        }
        
        if new_status not in valid_transitions.get(old_status, []):
            raise ValueError(f"Invalid status transition: {old_status} -> {new_status}")
        
        # Update status
        delivery.status = new_status
        
        # Update timestamps
        if new_status == DeliveryStatus.PICKED_UP:
            delivery.picked_up_at = datetime.now(UTC)
        elif new_status == DeliveryStatus.IN_TRANSIT:
            delivery.in_transit_at = datetime.now(UTC)
        elif new_status == DeliveryStatus.DELIVERED:
            delivery.delivered_at = datetime.now(UTC)
            if delivery.picked_up_at:
                delivery.actual_time_minutes = (
                    delivery.delivered_at - delivery.picked_up_at
                ).total_seconds() / 60
        elif new_status == DeliveryStatus.FAILED:
            delivery.failure_reason = status_request.notes
        
        # Update location if provided
        if status_request.location:
            delivery.current_location = status_request.location.model_dump()
        
        await self.db.flush()
        
        # Log status update
        await self._log_tracking_event(
            delivery.id,
            f"STATUS_UPDATE_{new_status.value}",
            old_status.value,
            new_status.value,
            delivery.current_location,
            notes=status_request.notes
        )
        
        # Update partner status if delivered
        if new_status == DeliveryStatus.DELIVERED and delivery.delivery_partner_id:
            partner = await self.get_delivery_partner(delivery.delivery_partner_id)
            if partner:
                partner.status = DeliveryPartnerStatus.AVAILABLE
                partner.total_deliveries = (partner.total_deliveries or 0) + 1
                partner.successful_deliveries = (partner.successful_deliveries or 0) + 1
        
        # Notify Order Service
        order_status_map = {
            DeliveryStatus.PICKED_UP: "OUT_FOR_DELIVERY",
            DeliveryStatus.IN_TRANSIT: "OUT_FOR_DELIVERY",
            DeliveryStatus.DELIVERED: "DELIVERED",
            DeliveryStatus.FAILED: "DELIVERY_FAILED",
        }
        if new_status in order_status_map:
            await self._update_order_delivery_status(
                delivery.order_id,
                order_status_map[new_status]
            )
        
        return delivery
    
    async def update_partner_location(
        self,
        partner_id: uuid.UUID,
        location: LocationSchema
    ):
        """Update delivery partner's current location"""
        partner = await self.get_delivery_partner(partner_id)
        if not partner:
            raise ValueError(f"Partner {partner_id} not found")
        
        partner.current_location = location.model_dump()
        partner.current_location["updated_at"] = datetime.now(UTC).isoformat()
        partner.last_active_at = datetime.now(UTC)
        
        await self.db.flush()
        
        # Update active deliveries
        result = await self.db.execute(
            select(Delivery).where(
                and_(
                    Delivery.delivery_partner_id == partner_id,
                    Delivery.status.in_([
                        DeliveryStatus.ASSIGNED,
                        DeliveryStatus.PICKED_UP,
                        DeliveryStatus.IN_TRANSIT
                    ])
                )
            )
        )
        active_deliveries = list(result.scalars().all())
        
        for delivery in active_deliveries:
            delivery.current_location = partner.current_location
            await self._log_tracking_event(
                delivery.id,
                "LOCATION_UPDATE",
                None,
                None,
                partner.current_location
            )
    
    async def get_delivery(self, delivery_id: uuid.UUID) -> Optional[Delivery]:
        """Get delivery by ID"""
        result = await self.db.execute(
            select(Delivery).where(Delivery.id == delivery_id)
        )
        return result.scalar_one_or_none()
    
    async def get_delivery_by_order(self, order_id: uuid.UUID) -> Optional[Delivery]:
        """Get delivery by order ID"""
        result = await self.db.execute(
            select(Delivery).where(Delivery.order_id == order_id)
        )
        return result.scalar_one_or_none()
    
    async def get_delivery_partner(self, partner_id: uuid.UUID) -> Optional[DeliveryPartner]:
        """Get delivery partner by ID"""
        result = await self.db.execute(
            select(DeliveryPartner).where(DeliveryPartner.id == partner_id)
        )
        return result.scalar_one_or_none()
    
    async def list_deliveries(
        self,
        status: Optional[DeliveryStatus] = None,
        partner_id: Optional[uuid.UUID] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> List[Delivery]:
        """List deliveries with filters"""
        query = select(Delivery).order_by(Delivery.created_at.desc())
        
        if status:
            query = query.where(Delivery.status == status)
        if partner_id:
            query = query.where(Delivery.delivery_partner_id == partner_id)
        
        query = query.offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_delivery_tracking(self, delivery_id: uuid.UUID) -> List[DeliveryTracking]:
        """Get delivery tracking history"""
        result = await self.db.execute(
            select(DeliveryTracking)
            .where(DeliveryTracking.delivery_id == delivery_id)
            .order_by(DeliveryTracking.created_at.asc())
        )
        return list(result.scalars().all())
    
    async def find_nearby_partners(
        self,
        location: Dict[str, float],
        radius_km: float = None
    ) -> List[DeliveryPartner]:
        """Find available partners near location"""
        radius = radius_km or settings.DELIVERY_PARTNER_SEARCH_RADIUS_KM
        
        # Get all available partners
        result = await self.db.execute(
            select(DeliveryPartner).where(
                and_(
                    DeliveryPartner.status == DeliveryPartnerStatus.AVAILABLE,
                    DeliveryPartner.is_active == True,
                    DeliveryPartner.is_verified == True,
                    DeliveryPartner.current_location.isnot(None)
                )
            )
        )
        all_partners = list(result.scalars().all())
        
        # Filter by distance
        nearby = []
        for partner in all_partners:
            if partner.current_location:
                distance = self._calculate_distance(location, partner.current_location)
                if distance <= radius:
                    nearby.append(partner)
        
        # Sort by distance
        nearby.sort(key=lambda p: self._calculate_distance(location, p.current_location))
        
        return nearby
    
    async def _find_nearest_available_partner(
        self,
        location: Dict[str, float]
    ) -> Optional[DeliveryPartner]:
        """Find the nearest available partner"""
        partners = await self.find_nearby_partners(location)
        return partners[0] if partners else None
    
    def _calculate_distance(self, loc1: Dict[str, float], loc2: Dict[str, float]) -> float:
        """Calculate distance between two coordinates in km"""
        try:
            return geodesic(
                (loc1.get('lat'), loc1.get('lng')),
                (loc2.get('lat'), loc2.get('lng'))
            ).kilometers
        except Exception as e:
            logger.error(f"Error calculating distance: {e}")
            return 0.0
    
    def _calculate_delivery_fee(self, distance_km: float) -> float:
        """Calculate delivery fee based on distance"""
        base_fee = settings.BASE_DELIVERY_FEE
        distance_fee = (distance_km - 2) * settings.PER_KM_FEE if distance_km > 2 else 0
        return max(base_fee, base_fee + distance_fee)
    
    def _calculate_eta(self, distance_km: float) -> float:
        """Calculate ETA in minutes"""
        return (distance_km / settings.AVERAGE_SPEED_KMH) * 60
    
    async def _log_tracking_event(
        self,
        delivery_id: uuid.UUID,
        event_type: str,
        status_from: Optional[str],
        status_to: Optional[str],
        location: Optional[Dict[str, Any]] = None,
        event_data: Optional[Dict[str, Any]] = None,
        notes: Optional[str] = None,
        triggered_by: str = "SYSTEM"
    ):
        """Log delivery tracking event"""
        tracking = DeliveryTracking(
            id=uuid.uuid4(),
            delivery_id=delivery_id,
            event_type=event_type,
            status_from=status_from,
            status_to=status_to,
            location=location,
            event_data=event_data,
            notes=notes,
            triggered_by=triggered_by,
        )
        self.db.add(tracking)
        await self.db.flush()
    
    async def _update_order_delivery_status(self, order_id: uuid.UUID, delivery_status: str):
        """Update order delivery status via Order Service API"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.patch(
                    f"{settings.ORDER_SERVICE_URL}/v1/orders/{order_id}/delivery-status",
                    json={"delivery_status": delivery_status},
                    timeout=10.0
                )
                if response.status_code != 200:
                    logger.error(f"Failed to update order delivery status: {response.text}")
        except Exception as e:
            logger.error(f"Error updating order delivery status: {e}")
