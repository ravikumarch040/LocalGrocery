"""__init__ for schemas"""
from app.api.v1.schemas.auth import (
    SendOTPRequest,
    VerifyOTPRequest,
    RefreshTokenRequest,
    TokenResponse,
    UserResponse,
    AuthResponse,
    OTPResponse
)

__all__ = [
    'SendOTPRequest',
    'VerifyOTPRequest',
    'RefreshTokenRequest',
    'TokenResponse',
    'UserResponse',
    'AuthResponse',
    'OTPResponse'
]
