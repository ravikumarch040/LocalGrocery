"""JWT Service - handles JWT token generation and validation"""
from datetime import datetime, timedelta, UTC
from typing import Optional, Dict
from jose import JWTError, jwt
import hashlib
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import User, RefreshToken
from app.config import get_settings

settings = get_settings()


class JWTService:
    """JWT token management service"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    def create_access_token(self, user_id: str, role: str) -> str:
        """
        Create JWT access token
        
        Args:
            user_id: User ID
            role: User role
        
        Returns:
            str: Encoded JWT token
        """
        expires_delta = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        expire = datetime.now(UTC) + expires_delta
        
        payload = {
            "sub": str(user_id),
            "role": role,
            "type": "access",
            "exp": expire,
            "iat": datetime.now(UTC)
        }
        
        return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    
    async def create_refresh_token(
        self,
        user_id: str,
        device_info: Optional[Dict] = None
    ) -> str:
        """
        Create and store refresh token
        
        Args:
            user_id: User ID
            device_info: Optional device information
        
        Returns:
            str: Encoded refresh token
        """
        expires_delta = timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
        expire = datetime.now(UTC) + expires_delta
        
        # Generate unique token
        token_data = f"{user_id}{datetime.now(UTC).isoformat()}"
        token_hash = hashlib.sha256(token_data.encode()).hexdigest()
        
        # Store refresh token in database
        refresh_token = RefreshToken(
            user_id=user_id,
            token_hash=token_hash,
            device_info=str(device_info) if device_info else None,
            expires_at=expire
        )
        self.db.add(refresh_token)
        await self.db.commit()
        await self.db.refresh(refresh_token)
        
        # Create JWT with token hash
        payload = {
            "sub": str(user_id),
            "token_hash": token_hash,
            "type": "refresh",
            "exp": expire,
            "iat": datetime.now(UTC)
        }
        
        return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    
    async def verify_access_token(self, token: str) -> Dict:
        """
        Verify and decode access token
        
        Args:
            token: JWT token
        
        Returns:
            dict: Decoded token payload
        
        Raises:
            JWTError: If token is invalid
        """
        try:
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
            
            if payload.get("type") != "access":
                raise JWTError("Invalid token type")
            
            return payload
        except JWTError as e:
            raise JWTError(f"Invalid token: {str(e)}")
    
    async def verify_refresh_token(self, token: str) -> Optional[User]:
        """
        Verify refresh token and return associated user
        
        Args:
            token: JWT refresh token
        
        Returns:
            User: User object if valid
        
        Raises:
            JWTError: If token is invalid or revoked
        """
        try:
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
            
            if payload.get("type") != "refresh":
                raise JWTError("Invalid token type")
            
            user_id = payload.get("sub")
            token_hash = payload.get("token_hash")
            
            # Check if refresh token exists and not revoked
            result = await self.db.execute(
                select(RefreshToken).where(
                    RefreshToken.token_hash == token_hash,
                    RefreshToken.user_id == user_id,
                    RefreshToken.is_revoked == False
                )
            )
            refresh_token = result.scalar_one_or_none()
            
            if not refresh_token:
                raise JWTError("Refresh token not found or revoked")
            
            # Check if expired (use timezone-aware datetime)
            if datetime.now(UTC) > refresh_token.expires_at:
                raise JWTError("Refresh token expired")
            
            # Get user
            user_result = await self.db.execute(
                select(User).where(User.id == user_id)
            )
            user = user_result.scalar_one_or_none()
            
            if not user or not user.is_active:
                raise JWTError("User not found or inactive")
            
            return user
            
        except JWTError as e:
            raise JWTError(f"Invalid refresh token: {str(e)}")
    
    async def revoke_refresh_token(self, token_hash: str) -> bool:
        """
        Revoke a refresh token
        
        Args:
            token_hash: Token hash to revoke
        
        Returns:
            bool: True if revoked successfully
        """
        result = await self.db.execute(
            select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        )
        token = result.scalar_one_or_none()
        
        if token:
            token.is_revoked = True
            await self.db.commit()
            return True
        
        return False
    
    async def revoke_all_user_tokens(self, user_id: str) -> int:
        """
        Revoke all refresh tokens for a user
        
        Args:
            user_id: User ID
        
        Returns:
            int: Number of tokens revoked
        """
        result = await self.db.execute(
            select(RefreshToken).where(
                RefreshToken.user_id == user_id,
                RefreshToken.is_revoked == False
            )
        )
        tokens = result.scalars().all()
        
        count = 0
        for token in tokens:
            token.is_revoked = True
            count += 1
        
        await self.db.commit()
        return count
