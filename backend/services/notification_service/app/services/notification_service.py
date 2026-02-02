"""Notification Service - Business logic for sending notifications"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, update
from app.models import Notification, DeviceToken, NotificationTemplate, NotificationPreference
from app.models import NotificationType, NotificationStatus, NotificationPriority
from app.api.v1.schemas.notifications import (
    SendSMSRequest, SendPushRequest, SendEmailRequest,
    RegisterDeviceTokenRequest, DeviceTypeEnum
)
from app.config import settings
from typing import Optional, List, Dict, Any
from datetime import datetime, UTC
import uuid
import logging
import httpx

logger = logging.getLogger(__name__)

# Lazy imports for optional dependencies
firebase_admin = None
msg91_client = None


class NotificationService:
    """Service for sending notifications"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def send_sms(self, request: SendSMSRequest) -> Notification:
        """Send SMS via MSG91"""
        # Create notification record
        notification = Notification(
            id=uuid.uuid4(),
            recipient_phone=request.phone,
            type=NotificationType.SMS,
            status=NotificationStatus.PENDING,
            priority=request.priority,
            template_id=request.template_id,
            message=request.message,
            reference_type=request.reference_type,
            reference_id=request.reference_id,
        )
        
        self.db.add(notification)
        await self.db.flush()
        
        # Send SMS
        if settings.MSG91_ENABLED and settings.MSG91_AUTH_KEY:
            try:
                success, response = await self._send_msg91_sms(request.phone, request.message)
                
                if success:
                    notification.status = NotificationStatus.SENT
                    notification.sent_at = datetime.now(UTC)
                    notification.provider_response = response
                    notification.provider_message_id = response.get('request_id')
                else:
                    notification.status = NotificationStatus.FAILED
                    notification.failed_at = datetime.now(UTC)
                    notification.error_message = str(response)
            except Exception as e:
                logger.error(f"Failed to send SMS: {e}")
                notification.status = NotificationStatus.FAILED
                notification.failed_at = datetime.now(UTC)
                notification.error_message = str(e)
        else:
            # Mock mode for development
            logger.info(f"[MOCK] SMS to {request.phone}: {request.message}")
            notification.status = NotificationStatus.SENT
            notification.sent_at = datetime.now(UTC)
            notification.provider_message_id = f"mock_{uuid.uuid4()}"
        
        await self.db.flush()
        return notification
    
    async def send_push(self, request: SendPushRequest) -> Notification:
        """Send push notification via FCM"""
        # Get FCM tokens
        fcm_tokens = []
        if request.fcm_token:
            fcm_tokens = [request.fcm_token]
        elif request.user_id:
            tokens = await self._get_user_fcm_tokens(request.user_id)
            fcm_tokens = [t.fcm_token for t in tokens]
        
        if not fcm_tokens:
            raise ValueError("No FCM tokens found for user")
        
        # Create notification record
        notification = Notification(
            id=uuid.uuid4(),
            user_id=request.user_id,
            fcm_token=fcm_tokens[0] if fcm_tokens else None,
            type=NotificationType.PUSH,
            status=NotificationStatus.PENDING,
            priority=request.priority,
            subject=request.title,
            message=request.body,
            data=request.data,
            reference_type=request.reference_type,
            reference_id=request.reference_id,
        )
        
        self.db.add(notification)
        await self.db.flush()
        
        # Send push
        if settings.FCM_ENABLED and settings.FIREBASE_CREDENTIALS_PATH:
            try:
                success, response = await self._send_fcm_push(
                    fcm_tokens,
                    request.title,
                    request.body,
                    request.data
                )
                
                if success:
                    notification.status = NotificationStatus.SENT
                    notification.sent_at = datetime.now(UTC)
                    notification.provider_response = response
                else:
                    notification.status = NotificationStatus.FAILED
                    notification.failed_at = datetime.now(UTC)
                    notification.error_message = str(response)
            except Exception as e:
                logger.error(f"Failed to send push: {e}")
                notification.status = NotificationStatus.FAILED
                notification.failed_at = datetime.now(UTC)
                notification.error_message = str(e)
        else:
            # Mock mode for development
            logger.info(f"[MOCK] PUSH to {request.user_id}: {request.title} - {request.body}")
            notification.status = NotificationStatus.SENT
            notification.sent_at = datetime.now(UTC)
            notification.provider_message_id = f"mock_{uuid.uuid4()}"
        
        await self.db.flush()
        return notification
    
    async def send_email(self, request: SendEmailRequest) -> Notification:
        """Send email (placeholder - implement with SendGrid/SES)"""
        notification = Notification(
            id=uuid.uuid4(),
            recipient_email=request.email,
            type=NotificationType.EMAIL,
            status=NotificationStatus.PENDING,
            subject=request.subject,
            message=request.body,
            template_id=request.template_id,
            reference_type=request.reference_type,
            reference_id=request.reference_id,
        )
        
        self.db.add(notification)
        await self.db.flush()
        
        # Mock email send
        logger.info(f"[MOCK] EMAIL to {request.email}: {request.subject}")
        notification.status = NotificationStatus.SENT
        notification.sent_at = datetime.now(UTC)
        notification.provider_message_id = f"mock_{uuid.uuid4()}"
        
        await self.db.flush()
        return notification
    
    async def register_device_token(self, request: RegisterDeviceTokenRequest) -> DeviceToken:
        """Register or update FCM device token"""
        # Check if token exists
        result = await self.db.execute(
            select(DeviceToken).where(DeviceToken.fcm_token == request.fcm_token)
        )
        token = result.scalar_one_or_none()
        
        if token:
            # Update existing token
            token.user_id = request.user_id
            token.device_type = request.device_type.value
            token.is_active = True
            token.last_used_at = datetime.now(UTC)
            token.device_info = request.device_info
        else:
            # Create new token
            token = DeviceToken(
                id=uuid.uuid4(),
                user_id=request.user_id,
                device_type=request.device_type.value,
                fcm_token=request.fcm_token,
                is_active=True,
                last_used_at=datetime.now(UTC),
                device_info=request.device_info
            )
            self.db.add(token)
        
        await self.db.flush()
        return token
    
    async def get_user_preferences(self, user_id: uuid.UUID) -> Optional[NotificationPreference]:
        """Get user notification preferences"""
        result = await self.db.execute(
            select(NotificationPreference).where(NotificationPreference.user_id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def update_user_preferences(
        self,
        user_id: uuid.UUID,
        preferences: Dict[str, bool]
    ) -> NotificationPreference:
        """Update user notification preferences"""
        result = await self.db.execute(
            select(NotificationPreference).where(NotificationPreference.user_id == user_id)
        )
        pref = result.scalar_one_or_none()
        
        if not pref:
            pref = NotificationPreference(
                id=uuid.uuid4(),
                user_id=user_id
            )
            self.db.add(pref)
        
        # Update fields
        for key, value in preferences.items():
            if hasattr(pref, key) and value is not None:
                setattr(pref, key, value)
        
        await self.db.flush()
        return pref
    
    async def get_notification(self, notification_id: uuid.UUID) -> Optional[Notification]:
        """Get notification by ID"""
        result = await self.db.execute(
            select(Notification).where(Notification.id == notification_id)
        )
        return result.scalar_one_or_none()
    
    async def list_notifications(
        self,
        user_id: Optional[uuid.UUID] = None,
        type: Optional[NotificationType] = None,
        status: Optional[NotificationStatus] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[Notification]:
        """List notifications with filters"""
        query = select(Notification).order_by(Notification.created_at.desc())
        
        if user_id:
            query = query.where(Notification.user_id == user_id)
        if type:
            query = query.where(Notification.type == type)
        if status:
            query = query.where(Notification.status == status)
        
        query = query.offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def _get_user_fcm_tokens(self, user_id: uuid.UUID) -> List[DeviceToken]:
        """Get active FCM tokens for user"""
        result = await self.db.execute(
            select(DeviceToken).where(
                and_(
                    DeviceToken.user_id == user_id,
                    DeviceToken.is_active == True
                )
            )
        )
        return list(result.scalars().all())
    
    async def _send_msg91_sms(self, phone: str, message: str) -> tuple[bool, Dict[str, Any]]:
        """Send SMS via MSG91 API"""
        url = "https://api.msg91.com/api/v5/flow/"
        
        # Remove + from phone if present
        phone = phone.lstrip('+')
        
        payload = {
            "sender": settings.MSG91_SENDER_ID,
            "route": settings.MSG91_ROUTE,
            "country": settings.MSG91_COUNTRY,
            "sms": [
                {
                    "message": message,
                    "to": [phone]
                }
            ]
        }
        
        headers = {
            "authkey": settings.MSG91_AUTH_KEY,
            "content-type": "application/json"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, headers=headers, timeout=10.0)
                
                if response.status_code == 200:
                    return True, response.json()
                else:
                    return False, {"error": response.text}
        except Exception as e:
            logger.error(f"MSG91 API error: {e}")
            return False, {"error": str(e)}
    
    async def _send_fcm_push(
        self,
        tokens: List[str],
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None
    ) -> tuple[bool, Dict[str, Any]]:
        """Send push notification via FCM"""
        try:
            global firebase_admin
            if firebase_admin is None:
                import firebase_admin
                from firebase_admin import credentials, messaging
                
                # Initialize Firebase (only once)
                if not firebase_admin._apps:
                    cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
                    firebase_admin.initialize_app(cred)
            
            from firebase_admin import messaging
            
            # Create message
            message = messaging.MulticastMessage(
                notification=messaging.Notification(
                    title=title,
                    body=body
                ),
                data=data or {},
                tokens=tokens
            )
            
            # Send
            response = messaging.send_multicast(message)
            
            return response.success_count > 0, {
                "success_count": response.success_count,
                "failure_count": response.failure_count
            }
        except Exception as e:
            logger.error(f"FCM error: {e}")
            return False, {"error": str(e)}
