# Notification Service

Multi-channel notification service for LocalGrocery platform supporting SMS, Push notifications, and Email.

## Features

- **SMS Notifications:** MSG91 integration for OTP and transactional messages
- **Push Notifications:** Firebase Cloud Messaging (FCM) for mobile apps
- **Email Notifications:** Email delivery (placeholder for SendGrid/SES)
- **Device Management:** FCM token registration and management
- **User Preferences:** Granular notification preferences by category
- **Templates:** Pre-defined message templates
- **Delivery Tracking:** Complete audit trail for all notifications
- **Retry Logic:** Automatic retry for failed notifications

## API Endpoints

### Notifications

- `POST /v1/notifications/sms` - Send SMS
- `POST /v1/notifications/push` - Send push notification
- `POST /v1/notifications/email` - Send email
- `GET /v1/notifications` - List notifications (with filters)
- `GET /v1/notifications/{id}` - Get notification details

### Device Management

- `POST /v1/notifications/device-tokens` - Register FCM token

### User Preferences

- `GET /v1/notifications/users/{user_id}/preferences` - Get preferences
- `PATCH /v1/notifications/users/{user_id}/preferences` - Update preferences

## Setup

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Firebase project (for FCM)
- MSG91 account (for SMS)

### Installation

```powershell
# Navigate to service directory
cd backend\services\notification_service

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Create `.env` file:

```env
# Database
DATABASE_URL=postgresql+asyncpg://localgrocery:password@localhost:5432/localgrocery

# Firebase (for push notifications)
FIREBASE_CREDENTIALS_PATH=/path/to/firebase-service-account.json
FCM_ENABLED=true

# MSG91 (for SMS)
MSG91_AUTH_KEY=your_auth_key_here
MSG91_SENDER_ID=LOCGRO
MSG91_ENABLED=true
```

### Firebase Setup

1. Create Firebase project at https://console.firebase.google.com
2. Generate service account key (Project Settings → Service Accounts)
3. Download JSON file and set path in `FIREBASE_CREDENTIALS_PATH`

### MSG91 Setup

1. Sign up at https://msg91.com
2. Get Auth Key from dashboard
3. Configure sender ID (6 characters)
4. Set environment variables

## Running

```powershell
# Development mode
python -m uvicorn app.main:app --reload --port 8006

# Production mode
python -m uvicorn app.main:app --host 0.0.0.0 --port 8006
```

## Usage Examples

### Send SMS

```bash
curl -X POST http://localhost:8006/v1/notifications/sms \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+919876543210",
    "message": "Your OTP is 123456",
    "priority": "HIGH"
  }'
```

### Send Push Notification

```bash
curl -X POST http://localhost:8006/v1/notifications/push \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "uuid-here",
    "title": "Order Delivered",
    "body": "Your order #12345 has been delivered",
    "data": {"order_id": "uuid", "action": "view_order"}
  }'
```

### Register Device Token

```bash
curl -X POST http://localhost:8006/v1/notifications/device-tokens \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "uuid-here",
    "fcm_token": "firebase-token-here",
    "device_type": "ANDROID"
  }'
```

## Database Schema

### notifications

- Complete notification log with delivery status
- Tracks SMS, Push, Email
- Provider responses and error messages
- Retry tracking

### device_tokens

- FCM tokens for push notifications
- Device type and metadata
- Active/inactive status

### notification_preferences

- Per-user notification preferences
- Granular control by category (orders, payments, delivery, promotional)
- Separate toggles for SMS, Push, Email

### notification_templates

- Pre-defined message templates
- Template variables for personalization

## Notification Types

1. **Transactional:**
   - OTP for authentication
   - Order confirmations
   - Payment receipts
   - Delivery updates

2. **Promotional:**
   - Offers and discounts
   - New product launches
   - Marketing campaigns

3. **System:**
   - Account updates
   - Security alerts
   - Service notifications

## Integration with Other Services

### Auth Service
- OTP delivery for login/signup

### Order Service
- Order status updates (placed, confirmed, packed, shipped)

### Payment Service
- Payment confirmations
- Failed payment alerts

### Delivery Service
- Delivery tracking updates
- Partner assignment notifications

## Testing

```powershell
# Run tests
pytest

# With coverage
pytest --cov=app --cov-report=html
```

## Monitoring

Key metrics to track:
- SMS delivery rate
- Push notification delivery rate
- Failed notifications count
- Average delivery time
- Provider response times

## Production Checklist

- [ ] Set up Firebase project with production credentials
- [ ] Configure MSG91 account with production auth key
- [ ] Set up email provider (SendGrid/AWS SES)
- [ ] Enable retry logic for failed notifications
- [ ] Configure rate limiting for bulk notifications
- [ ] Set up monitoring and alerts
- [ ] Implement notification queue (Redis/RabbitMQ)
- [ ] Add webhook receivers for delivery status

## License

Proprietary - LocalGrocery Platform
