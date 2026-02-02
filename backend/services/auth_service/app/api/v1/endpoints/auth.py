"""Authentication endpoints"""
from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError

from app.database import get_db
from app.services import AuthService
from app.api.v1.schemas.auth import (
    SendOTPRequest,
    SendOTPResponse,
    VerifyOTPRequest,
    TokenResponse,
    RefreshTokenRequest,
    LogoutResponse,
    UserProfileResponse
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/send-otp", response_model=SendOTPResponse)
async def send_otp(
    request: SendOTPRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Send OTP to phone number for authentication
    
    - **phone**: Phone number with country code (e.g., +919876543210)
    - **purpose**: Purpose of OTP (LOGIN, VERIFY_PHONE, etc.)
    """
    try:
        auth_service = AuthService(db)
        success = await auth_service.send_otp(request.phone, request.purpose or "LOGIN")
        await db.commit()  # Ensure transaction is committed
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Failed to send OTP. Please try again."
            )
        
        return SendOTPResponse(
            success=True,
            message=f"OTP sent successfully to {request.phone}"
        )
    
    except ValueError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=str(e)
        )
    except Exception as e:
        await db.rollback()
        import traceback
        print(f"[send_otp] Internal error: {e}")
        print(f"[send_otp] Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/verify-otp", response_model=TokenResponse)
async def verify_otp(
    request: VerifyOTPRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Verify OTP and login/register user
    
    - **phone**: Phone number with country code
    - **otp**: 6-digit OTP code
    - **name**: User name (optional, for new registrations)
    - **role**: User role (CUSTOMER, RETAILER, DELIVERY_PARTNER)
    - **device_info**: Optional device information
    
    Returns JWT access token and refresh token
    """
    try:
        auth_service = AuthService(db)
        token_response = await auth_service.verify_otp_and_login(
            phone=request.phone,
            otp_code=request.otp,
            name=request.name,
            role=request.role,
            device_info=request.device_info
        )
        await db.commit()  # Ensure transaction is committed
        
        return token_response
    
    except ValueError as e:
        await db.rollback()
        print(f"[verify_otp] ValueError: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        await db.rollback()
        import traceback
        print(f"[verify_otp] Exception type: {type(e).__name__}")
        print(f"[verify_otp] Exception message: {str(e)}")
        print(f"[verify_otp] Traceback:\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Refresh access token using refresh token
    
    - **refresh_token**: Valid refresh token
    
    Returns new access token (same refresh token)
    """
    try:
        auth_service = AuthService(db)
        token_response = await auth_service.refresh_access_token(request.refresh_token)
        
        return token_response
    
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired refresh token: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/logout", response_model=LogoutResponse)
async def logout(
    authorization: str = Header(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Logout current session (revoke refresh token)
    
    Requires: Authorization header with Bearer token
    """
    try:
        # Extract token from header
        if not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization header format"
            )
        
        token = authorization.replace("Bearer ", "")
        
        # Decode token to get token_hash (simplified - in production, pass refresh token)
        # For now, we'll implement basic logout
        from jose import jwt
        from app.config import get_settings
        
        settings = get_settings()
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        token_hash = payload.get("token_hash")
        
        if not token_hash:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token - no hash found"
            )
        
        auth_service = AuthService(db)
        success = await auth_service.logout(token_hash)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Token not found or already revoked"
            )
        
        return LogoutResponse(
            success=True,
            message="Logged out successfully"
        )
    
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/me", response_model=UserProfileResponse)
async def get_current_user(
    authorization: str = Header(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current user profile
    
    Requires: Authorization header with Bearer access token
    """
    try:
        # Extract and verify token
        if not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization header format"
            )
        
        token = authorization.replace("Bearer ", "")
        
        auth_service = AuthService(db)
        payload = await auth_service.jwt_service.verify_access_token(token)
        
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        # Get user
        user = await auth_service.get_user_by_id(user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return UserProfileResponse(
            id=str(user.id),
            phone=user.phone,
            name=user.full_name,
            email=user.email,
            role=user.role,
            is_active=user.is_active,
            is_phone_verified=user.phone_verified,
            created_at=user.created_at
        )
    
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired token: {str(e)}"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )
