"""Notification endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.notification_service import NotificationService
from app.models import NotificationType, NotificationStatus
from app.api.v1.schemas.notifications import (
    SendSMSRequest, SendPushRequest, SendEmailRequest,
    RegisterDeviceTokenRequest, UpdatePreferencesRequest,
    NotificationResponse, DeviceTokenResponse, NotificationPreferenceResponse,
    SendResponse,
)
from typing import List, Optional
import uuid

router = APIRouter()


@router.post("/sms", response_model=SendResponse)
async def send_sms(
    request: SendSMSRequest,
    db: AsyncSession = Depends(get_db)
):
    """Send SMS notification"""
    service = NotificationService(db)
    
    try:
        notification = await service.send_sms(request)
        await db.commit()
        await db.refresh(notification)
        
        return SendResponse(
            success=notification.status == NotificationStatus.SENT,
            notification_id=notification.id,
            message="SMS sent successfully" if notification.status == NotificationStatus.SENT else "SMS failed",
            provider_message_id=notification.provider_message_id
        )
    except ValueError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/push", response_model=SendResponse)
async def send_push(
    request: SendPushRequest,
    db: AsyncSession = Depends(get_db)
):
    """Send push notification"""
    service = NotificationService(db)
    
    try:
        notification = await service.send_push(request)
        await db.commit()
        await db.refresh(notification)
        
        return SendResponse(
            success=notification.status == NotificationStatus.SENT,
            notification_id=notification.id,
            message="Push sent successfully" if notification.status == NotificationStatus.SENT else "Push failed",
            provider_message_id=notification.provider_message_id
        )
    except ValueError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/email", response_model=SendResponse)
async def send_email(
    request: SendEmailRequest,
    db: AsyncSession = Depends(get_db)
):
    """Send email notification"""
    service = NotificationService(db)
    
    try:
        notification = await service.send_email(request)
        await db.commit()
        await db.refresh(notification)
        
        return SendResponse(
            success=notification.status == NotificationStatus.SENT,
            notification_id=notification.id,
            message="Email sent successfully" if notification.status == NotificationStatus.SENT else "Email failed",
            provider_message_id=notification.provider_message_id
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/device-tokens", response_model=DeviceTokenResponse, status_code=status.HTTP_201_CREATED)
async def register_device_token(
    request: RegisterDeviceTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """Register FCM device token"""
    service = NotificationService(db)
    
    try:
        token = await service.register_device_token(request)
        await db.commit()
        await db.refresh(token)
        return token
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{notification_id}", response_model=NotificationResponse)
async def get_notification(
    notification_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get notification by ID"""
    service = NotificationService(db)
    
    notification = await service.get_notification(notification_id)
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Notification {notification_id} not found"
        )
    
    return notification


@router.get("", response_model=List[NotificationResponse])
async def list_notifications(
    user_id: Optional[uuid.UUID] = None,
    type: Optional[str] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """List notifications with filters"""
    service = NotificationService(db)
    
    try:
        # Parse enums if provided
        notification_type = None
        if type:
            try:
                notification_type = NotificationType(type)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid type: {type}"
                )
        
        notification_status = None
        if status_filter:
            try:
                notification_status = NotificationStatus(status_filter)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid status: {status_filter}"
                )
        
        notifications = await service.list_notifications(
            user_id=user_id,
            type=notification_type,
            status=notification_status,
            skip=skip,
            limit=limit
        )
        
        return notifications
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/users/{user_id}/preferences", response_model=NotificationPreferenceResponse)
async def get_user_preferences(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get user notification preferences"""
    service = NotificationService(db)
    
    preferences = await service.get_user_preferences(user_id)
    if not preferences:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Preferences not found for user {user_id}"
        )
    
    return preferences


@router.patch("/users/{user_id}/preferences", response_model=NotificationPreferenceResponse)
async def update_user_preferences(
    user_id: uuid.UUID,
    request: UpdatePreferencesRequest,
    db: AsyncSession = Depends(get_db)
):
    """Update user notification preferences"""
    service = NotificationService(db)
    
    try:
        # Convert request to dict, excluding None values
        prefs_dict = request.model_dump(exclude_none=True)
        
        preferences = await service.update_user_preferences(user_id, prefs_dict)
        await db.commit()
        await db.refresh(preferences)
        return preferences
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
