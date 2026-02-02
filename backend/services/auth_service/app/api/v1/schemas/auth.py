"""Pydantic schemas for request/response validation"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
import re


class SendOTPRequest(BaseModel):
    """Request to send OTP"""
    phone: str = Field(..., min_length=10, max_length=15, description="Phone number with country code")
    purpose: str = Field(default="LOGIN", description="Purpose of OTP")
    
    model_config = {"validate_default": True}
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        # Basic Indian phone number validation
        v = v.strip()
        
        # Remove all non-digit characters except +
        cleaned = ''.join(c for c in v if c.isdigit() or c == '+')
        
        # Pattern: Optional +, Optional 91, then 10 digit number starting with 6-9
        if not re.match(r'^\+?91?[6-9]\d{9}$', cleaned):
            raise ValueError('Invalid phone number format. Must be a valid Indian mobile number')
        
        # Normalize to +91 format
        if not cleaned.startswith('+'):
            # Remove leading 91 if present
            if cleaned.startswith('91'):
                cleaned = cleaned[2:]
            v = '+91' + cleaned
        else:
            v = cleaned
        
        return v


class SendOTPResponse(BaseModel):
    """Response after sending OTP"""
    success: bool
    message: str


class VerifyOTPRequest(BaseModel):
    """Request to verify OTP"""
    phone: str = Field(..., min_length=10, max_length=15)
    otp: str = Field(..., min_length=6, max_length=6, description="6-digit OTP")
    name: Optional[str] = Field(None, min_length=2, max_length=100, description="User name for new registrations")
    role: str = Field(default="CUSTOMER", description="User role: CUSTOMER, RETAILER, DELIVERY_PARTNER, ADMIN")
    device_info: Optional[dict] = Field(None, description="Optional device information")
    
    @field_validator('role')
    @classmethod
    def validate_role(cls, v):
        valid_roles = ['CUSTOMER', 'RETAILER', 'DELIVERY_PARTNER', 'ADMIN']
        if v.upper() not in valid_roles:
            raise ValueError(f'Role must be one of: {", ".join(valid_roles)}')
        return v.upper()
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        v = v.strip()
        # Normalize by removing non-digits except '+'
        cleaned = ''.join(c for c in v if c.isdigit() or c == '+')
        if not re.match(r'^\+?91?[6-9]\d{9}$', cleaned):
            raise ValueError('Invalid phone number format')
        if not cleaned.startswith('+'):
            if cleaned.startswith('91'):
                cleaned = cleaned[2:]
            v = '+91' + cleaned
        else:
            v = cleaned
        return v

    @field_validator('otp')
    @classmethod
    def validate_otp_numeric(cls, v):
        if not v.isdigit():
            raise ValueError('OTP must be numeric')
        return v


class RefreshTokenRequest(BaseModel):
    """Request to refresh access token"""
    refresh_token: str = Field(..., min_length=10)


class UserResponse(BaseModel):
    """User profile response"""
    id: str
    phone: str
    full_name: str
    email: Optional[str] = None
    avatar: Optional[str] = None
    role: str
    is_active: bool = True
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """JWT token response - matches Flutter AuthResponse model"""
    access_token: str
    refresh_token: str
    expires_in: int = 900  # 15 minutes in seconds
    user: UserResponse





class LogoutResponse(BaseModel):
    """Response after logout"""
    success: bool
    message: str


class UserProfileResponse(BaseModel):
    """User profile response"""
    id: str
    phone: str
    name: str
    email: Optional[str]
    role: str
    is_active: bool
    is_phone_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# Legacy responses for compatibility
class UserResponse(BaseModel):
    """User information response"""
    id: str
    phone: str
    role: str
    full_name: Optional[str] = None
    email: Optional[str] = None
    profile_image_url: Optional[str] = None
    phone_verified: bool
    is_active: bool
    last_login_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class AuthResponse(BaseModel):
    """Complete authentication response"""
    success: bool
    message: str
    data: Optional[dict] = None
    tokens: Optional[TokenResponse] = None
    user: Optional[UserResponse] = None


class OTPResponse(BaseModel):
    """OTP send response"""
    success: bool
    message: str
    data: Optional[dict] = None

