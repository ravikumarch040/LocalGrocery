"""Delivery Partner endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.delivery_service import DeliveryService
from app.models import DeliveryPartnerStatus
from app.api.v1.schemas.deliveries import (
    DeliveryPartnerResponse,
    UpdatePartnerLocationRequest,
    UpdatePartnerStatusRequest,
    LocationSchema,
)
from typing import List, Optional
import uuid

router = APIRouter()


@router.get("/nearby", response_model=List[DeliveryPartnerResponse])
async def find_nearby_partners(
    lat: float = Query(..., ge=-90, le=90),
    lng: float = Query(..., ge=-180, le=180),
    radius_km: Optional[float] = Query(None, gt=0, le=50),
    db: AsyncSession = Depends(get_db)
):
    """Find nearby available delivery partners"""
    service = DeliveryService(db)
    
    try:
        location = {"lat": lat, "lng": lng}
        partners = await service.find_nearby_partners(location, radius_km)
        return partners
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{partner_id}", response_model=DeliveryPartnerResponse)
async def get_delivery_partner(
    partner_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get delivery partner details"""
    service = DeliveryService(db)
    
    partner = await service.get_delivery_partner(partner_id)
    if not partner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Partner {partner_id} not found"
        )
    
    return partner


@router.patch("/{partner_id}/location", status_code=status.HTTP_200_OK)
async def update_partner_location(
    partner_id: uuid.UUID,
    request: UpdatePartnerLocationRequest,
    db: AsyncSession = Depends(get_db)
):
    """Update delivery partner's current location"""
    service = DeliveryService(db)
    
    try:
        await service.update_partner_location(partner_id, request.location)
        await db.commit()
        return {"message": "Location updated successfully"}
    except ValueError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.patch("/{partner_id}/status", response_model=DeliveryPartnerResponse)
async def update_partner_status(
    partner_id: uuid.UUID,
    request: UpdatePartnerStatusRequest,
    db: AsyncSession = Depends(get_db)
):
    """Update delivery partner availability status"""
    service = DeliveryService(db)
    
    try:
        partner = await service.get_delivery_partner(partner_id)
        if not partner:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Partner {partner_id} not found"
            )
        
        # Update status
        try:
            new_status = DeliveryPartnerStatus(request.status.value)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {request.status.value}"
            )
        
        partner.status = new_status
        
        await db.commit()
        await db.refresh(partner)
        return partner
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
