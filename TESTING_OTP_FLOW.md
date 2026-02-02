# Testing OTP Authentication - Fixed

## Issues Fixed

1. **Phone Number Limit**: UI was limiting to 10 digits only
   - ✅ Updated to allow 10-15 characters (supporting `+91XXXXXXXXXX` format)

2. **API Endpoint Path**: Was using `/auth/otp/send` instead of `/v1/auth/send-otp`
   - ✅ Corrected endpoint paths to match backend

3. **Phone Number Format**: Backend expects country code
   - ✅ Added automatic normalization from UI (10-digit or +91 format)

4. **Request Field Name**: Was using `phone_number` instead of `phone`
   - ✅ Updated request body to use `phone` field

## Testing Steps

### 1. Start Backend Service
```powershell
# In backend directory
cd services\auth_service
python -m uvicorn app.main:app --reload --port 8001
```

### 2. Run Flutter App
```powershell
# In customer_app directory
cd apps\customer_app
flutter run -d windows
```

### 3. Test OTP Flow

**Option A: Using 10-digit number**
- Enter: `9876543210`
- App normalizes to: `+919876543210`
- Click "Send OTP"

**Option B: Using country code format**
- Enter: `+919876543210`
- App normalizes and sends as is
- Click "Send OTP"

**Option C: Using 91 prefix**
- Enter: `919876543210`
- App normalizes to: `+919876543210`
- Click "Send OTP"

### 4. Verify OTP

Default test OTP in backend: **123456**

- Phone: `9876543210` (or with any format above)
- OTP: `123456`
- Click "Verify"

## What Changed

### Frontend (Flutter)

**1. Login Screen** (`apps/customer_app/lib/screens/auth/login_screen.dart`)
- Changed maxLength from 10 to 15 characters
- Updated hint text to show both formats
- Better error messages showing backend URL for debugging

**2. Phone Validator** (`packages/core/lib/src/utils/validators.dart`)
- Now accepts both formats: `XXXXXXXXXX` and `+91XXXXXXXXXX`
- Handles phone numbers with or without country code

**3. Auth Service** (`packages/api_client/lib/src/services/auth_service.dart`)
- Added `_normalizePhoneNumber()` method
- Converts any input format to `+91XXXXXXXXXX`
- Updated endpoints to `/v1/auth/send-otp` and `/v1/auth/verify-otp`
- Changed request field from `phone_number` to `phone`

## Testing Edge Cases

| Input | Normalized | Status |
|-------|-----------|--------|
| `9876543210` | `+919876543210` | ✅ Works |
| `+919876543210` | `+919876543210` | ✅ Works |
| `919876543210` | `+919876543210` | ✅ Works |
| `98-7654-3210` | `+919876543210` | ✅ Works |
| `9876543` | ❌ | Invalid (too short) |
| `1234567890` | ❌ | Invalid (must start 6-9) |

## Backend Validation Rules

From `backend/services/auth_service/app/api/v1/schemas/auth.py`:
- Phone must be 10-15 characters total
- Must match pattern: `^(\+91)?[6-9]\d{9}$`
- Indian mobile numbers only (start with 6-9)
- Automatically normalized to `+91` format by backend

## Debugging

If still seeing "Failed to send OTP" error:

1. **Check backend is running:**
   ```bash
   curl http://localhost:8001/docs
   ```

2. **Check app logs:**
   - Look for: `[SendOTP Error: ...]` or `[SendOTP Exception: ...]`
   - These will show the actual error from backend

3. **Test backend directly:**
   ```bash
   curl -X POST http://localhost:8001/v1/auth/send-otp \
     -H "Content-Type: application/json" \
     -d '{"phone": "+919876543210", "purpose": "LOGIN"}'
   ```

4. **Check network:**
   - Verify localhost:8001 is accessible
   - Check firewall settings
