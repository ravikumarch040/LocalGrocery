"""Auth Service - orchestrates authentication flows"""
from typing import Optional, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import User
from app.services.otp_service import OTPService
from app.services.jwt_service import JWTService
from app.api.v1.schemas.auth import TokenResponse


class AuthService:
    """
    Main authentication service - coordinates OTP and JWT operations
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.otp_service = OTPService(db)
        self.jwt_service = JWTService(db)
    
    async def send_otp(self, phone: str, purpose: str = "LOGIN") -> bool:
        """
        Send OTP to phone number
        
        Args:
            phone: Phone number with country code
            purpose: Purpose of OTP
        
        Returns:
            bool: True if OTP sent successfully
        
        Raises:
            ValueError: If rate limit exceeded
        """
        # Ensure purpose is not None
        if not purpose:
            purpose = "LOGIN"
        
        # Check rate limit
        if not await self.otp_service.check_rate_limit(phone):
            raise ValueError("Too many OTP requests. Please try again later.")
        
        # Generate OTP
        otp_code = await self.otp_service.generate_otp(phone, purpose)
        
        # Send via SMS (use the method name consistently)
        return await self.otp_service.send_otp_sms(phone, otp_code)
    
    async def verify_otp_and_login(
        self,
        phone: str,
        otp_code: str,
        name: Optional[str] = None,
        role: str = "CUSTOMER",
        device_info: Optional[Dict] = None
    ) -> TokenResponse:
        """
        Verify OTP and create/login user
        
        Args:
            phone: Phone number with country code
            otp_code: OTP to verify
            name: User name (for new users)
            role: User role
            device_info: Optional device information
        
        Returns:
            TokenResponse: Access and refresh tokens
        
        Raises:
            ValueError: If OTP verification fails
        """
        # Verify OTP
        await self.otp_service.verify_otp(phone, otp_code, "LOGIN")
        
        # Find or create user
        result = await self.db.execute(
            select(User).where(User.phone == phone)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            # Create new user
            user = User(
                phone=phone,
                full_name=name or f"User {phone[-4:]}",
                role=role,
                phone_verified=True
            )
            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)
        else:
            # Update phone verification status
            if not user.phone_verified:
                user.phone_verified = True
                await self.db.commit()
        
        # Generate tokens
        access_token = self.jwt_service.create_access_token(
            user_id=str(user.id),
            role=user.role
        )
        refresh_token = await self.jwt_service.create_refresh_token(
            user_id=str(user.id),
            device_info=device_info
        )
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=900,  # 15 minutes
            user={
                "id": str(user.id),
                "phone": user.phone,
                "full_name": user.full_name,
                "email": user.email or None,
                "avatar": user.profile_image_url or None,  # Map profile_image_url to avatar
                "role": user.role,
                "is_active": user.is_active,
                "created_at": user.created_at,
            }
        )
    
    async def refresh_access_token(self, refresh_token: str) -> TokenResponse:
        """
        Generate new access token using refresh token
        
        Args:
            refresh_token: Valid refresh token
        
        Returns:
            TokenResponse: New access token (same refresh token)
        
        Raises:
            JWTError: If refresh token invalid
        """
        # Verify refresh token and get user
        user = await self.jwt_service.verify_refresh_token(refresh_token)
        
        # Generate new access token
        access_token = self.jwt_service.create_access_token(
            user_id=str(user.id),
            role=user.role
        )
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,  # Same refresh token
            expires_in=900,  # 15 minutes
            user={
                "id": str(user.id),
                "phone": user.phone,
                "full_name": user.full_name,
                "email": user.email or None,
                "avatar": user.profile_image_url or None,  # Map profile_image_url to avatar
                "role": user.role,
                "is_active": user.is_active,
                "created_at": user.created_at,
            }
        )
    
    async def logout(self, token_hash: str) -> bool:
        """
        Logout user by revoking refresh token
        
        Args:
            token_hash: Refresh token hash to revoke
        
        Returns:
            bool: True if logout successful
        """
        return await self.jwt_service.revoke_refresh_token(token_hash)
    
    async def logout_all_devices(self, user_id: str) -> int:
        """
        Logout user from all devices
        
        Args:
            user_id: User ID
        
        Returns:
            int: Number of devices logged out
        """
        return await self.jwt_service.revoke_all_user_tokens(user_id)
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """
        Get user by ID
        
        Args:
            user_id: User ID
        
        Returns:
            User: User object or None
        """
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
