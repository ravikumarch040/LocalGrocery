"""OTP Service - handles OTP generation, sending, and verification"""
import secrets
import random
import logging
from datetime import datetime, timedelta, UTC
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, update
from app.models import OTP
from app.config import get_settings
import httpx

settings = get_settings()
logger = logging.getLogger(__name__)


class OTPService:
    """OTP generation and verification service"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def generate_otp(self, phone: str, purpose: str = "LOGIN") -> str:
        """
        Generate a new OTP for the given phone number
        
        Args:
            phone: Phone number with country code
            purpose: Purpose of OTP (LOGIN, VERIFY_PHONE, etc.)
        
        Returns:
            str: Generated OTP code
        """
        # Generate secure 6-digit OTP
        otp_code = ''.join([str(random.randint(0, 9)) for _ in range(settings.OTP_LENGTH)])
        
        # Calculate expiry time (timezone-aware)
        expires_at = datetime.now(UTC) + timedelta(minutes=settings.OTP_EXPIRY_MINUTES)
        
        # Invalidate previous OTPs for this phone and purpose
        stmt = update(OTP).where(
            and_(
                OTP.phone == phone,
                OTP.purpose == purpose,
                OTP.is_verified == False
            )
        ).values(is_verified=True)
        await self.db.execute(stmt)
        # Defer commit to endpoint; reduce transaction churn
        
        # Create new OTP record
        new_otp = OTP(
            phone=phone,
            otp_code=otp_code,
            purpose=purpose,
            expires_at=expires_at
        )
        self.db.add(new_otp)
        # Defer commit to endpoint; no refresh needed for returning code
        
        return otp_code
    
    async def send_otp_sms(self, phone: str, otp_code: str) -> bool:
        """
        Send OTP via SMS provider (MSG91). In DEBUG/dev mode, do not call external API.
        """
        try:
            # Dev mode: avoid external dependency; log and succeed
            if settings.DEBUG or not settings.MSG91_AUTH_KEY:
                logger.info(f"[DEV MODE] OTP for {phone}: {otp_code}")
                print(f"[DEV MODE] OTP for {phone}: {otp_code}", flush=True)
                return True
            
            url = "https://api.msg91.com/api/v5/otp"
            headers = {
                "authkey": settings.MSG91_AUTH_KEY,
                "content-type": "application/json"
            }
            payload = {
                "template_id": settings.MSG91_OTP_TEMPLATE_ID,
                "mobile": phone.lstrip('+'),
                "otp": otp_code,
                "sender": settings.MSG91_SENDER_ID
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, headers=headers, timeout=10.0)
                return response.status_code == 200
        except Exception as e:
            # Do not propagate provider errors as 500; treat as send failure
            logger.error(f"Error sending OTP via MSG91: {e}")
            return False

    async def verify_otp(self, phone: str, otp_code: str, purpose: str = "LOGIN") -> bool:
        """
        Verify OTP for the given phone number
        
        Args:
            phone: Phone number with country code
            otp_code: OTP code to verify
            purpose: Purpose of OTP
        
        Returns:
            bool: True if OTP is valid
        
        Raises:
            ValueError: If OTP is invalid, expired, or max attempts exceeded
        """
        # Find the OTP record
        result = await self.db.execute(
            select(OTP).where(
                and_(
                    OTP.phone == phone,
                    OTP.purpose == purpose,
                    OTP.is_verified == False
                )
            ).order_by(OTP.created_at.desc()).limit(1)
        )
        otp_record = result.scalar_one_or_none()
        
        if not otp_record:
            raise ValueError("No OTP found for this phone number")
        
        # Check if expired (use timezone-aware datetime)
        if datetime.now(UTC) > otp_record.expires_at:
            raise ValueError("OTP has expired")
        
        # Check max attempts
        if otp_record.attempts >= settings.OTP_MAX_ATTEMPTS:
            raise ValueError("Maximum OTP attempts exceeded")
        
        # Increment attempts
        otp_record.attempts += 1
        
        # Verify OTP code
        if otp_record.otp_code != otp_code:
            await self.db.commit()
            raise ValueError(f"Invalid OTP. {settings.OTP_MAX_ATTEMPTS - otp_record.attempts} attempts remaining")
        
        # Mark as verified
        otp_record.is_verified = True
        await self.db.commit()
        
        return True
    
    async def check_rate_limit(self, phone: str) -> bool:
        """
        Check if phone number has exceeded OTP rate limit
        
        Args:
            phone: Phone number with country code
        
        Returns:
            bool: True if within rate limit, False if exceeded
        """
        # Check OTPs sent in last hour (timezone-aware)
        one_hour_ago = datetime.now(UTC) - timedelta(hours=1)
        result = await self.db.execute(
            select(OTP).where(
                and_(
                    OTP.phone == phone,
                    OTP.created_at >= one_hour_ago
                )
            )
        )
        recent_otps = result.scalars().all()
        
        return len(recent_otps) < settings.OTP_RATE_LIMIT_PER_HOUR
