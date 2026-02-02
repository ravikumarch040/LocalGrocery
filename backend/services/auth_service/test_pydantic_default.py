from pydantic import BaseModel, Field

class SendOTPRequest(BaseModel):
    phone: str = Field(..., min_length=10, max_length=15)
    purpose: str = Field(default="LOGIN", description="Purpose of OTP")
    
    model_config = {"validate_default": True}

# Test without providing purpose
req = SendOTPRequest(phone="+919876543211")
print(f"phone: {req.phone}")
print(f"purpose: {req.purpose}")
print(f"purpose is None: {req.purpose is None}")
