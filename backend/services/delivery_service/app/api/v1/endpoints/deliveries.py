"""Delivery endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.delivery_service import DeliveryService
from app.models import DeliveryStatus
from app.api.v1.schemas.deliveries import (
    DeliveryCreateRequest,
    AssignDeliveryRequest,
    UpdateDeliveryStatusRequest,
    DeliveryResponse,
    DeliveryTrackingResponse,
)
from typing import List, Optional
import uuid

router = APIRouter()


@router.post("", response_model=DeliveryResponse, status_code=status.HTTP_201_CREATED)
async def create_delivery(
    request: DeliveryCreateRequest,
    db: AsyncSession = Depends(get_db)
):
    """Create a new delivery for an order"""
    service = DeliveryService(db)
    
    try:
        delivery = await service.create_delivery(request)
        await db.commit()
        await db.refresh(delivery)
        return delivery
    except ValueError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/{delivery_id}/assign", response_model=DeliveryResponse)
async def assign_delivery(
    delivery_id: uuid.UUID,
    request: AssignDeliveryRequest,
    db: AsyncSession = Depends(get_db)
):
    """Assign delivery to a partner (auto or manual)"""
    service = DeliveryService(db)
    
    try:
        delivery = await service.assign_delivery_partner(
            delivery_id,
            request.delivery_partner_id
        )
        await db.commit()
        await db.refresh(delivery)
        return delivery
    except ValueError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.patch("/{delivery_id}/status", response_model=DeliveryResponse)
async def update_delivery_status(
    delivery_id: uuid.UUID,
    request: UpdateDeliveryStatusRequest,
    db: AsyncSession = Depends(get_db)
):
    """Update delivery status"""
    service = DeliveryService(db)
    
    try:
        delivery = await service.update_delivery_status(delivery_id, request)
        await db.commit()
        await db.refresh(delivery)
        return delivery
    except ValueError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{delivery_id}", response_model=DeliveryResponse)
async def get_delivery(
    delivery_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get delivery details by ID"""
    service = DeliveryService(db)
    
    delivery = await service.get_delivery(delivery_id)
    if not delivery:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Delivery {delivery_id} not found"
        )
    
    return delivery


@router.get("/order/{order_id}", response_model=DeliveryResponse)
async def get_delivery_by_order(
    order_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get delivery by order ID"""
    service = DeliveryService(db)
    
    delivery = await service.get_delivery_by_order(order_id)
    if not delivery:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No delivery found for order {order_id}"
        )
    
    return delivery


@router.get("", response_model=List[DeliveryResponse])
async def list_deliveries(
    status_filter: Optional[str] = Query(None, alias="status"),
    partner_id: Optional[uuid.UUID] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """List deliveries with filters"""
    service = DeliveryService(db)
    
    try:
        # Parse status if provided
        delivery_status = None
        if status_filter:
            try:
                delivery_status = DeliveryStatus(status_filter)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid status: {status_filter}"
                )
        
        deliveries = await service.list_deliveries(
            status=delivery_status,
            partner_id=partner_id,
            skip=skip,
            limit=limit
        )
        
        return deliveries
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{delivery_id}/tracking", response_model=List[DeliveryTrackingResponse])
async def get_delivery_tracking(
    delivery_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get delivery tracking history"""
    service = DeliveryService(db)
    
    # Verify delivery exists
    delivery = await service.get_delivery(delivery_id)
    if not delivery:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Delivery {delivery_id} not found"
        )
    
    tracking = await service.get_delivery_tracking(delivery_id)
    return tracking
