# Payment Service

Payment gateway integration and transaction management service for LocalGrocery platform.

## Overview

The Payment Service handles all payment-related operations including:
- Payment initiation with Razorpay and Cashfree gateways
- Payment verification and signature validation
- Webhook handling for payment status updates
- Refund processing
- Payment transaction audit logging
- Integration with Order Service for payment status updates

## Features

### Payment Methods
- **UPI**: Unified Payments Interface
- **Card**: Credit/Debit cards
- **Wallet**: Digital wallets (Paytm, PhonePe, etc.)
- **Net Banking**: Bank transfers
- **COD**: Cash on Delivery
- **BNPL**: Buy Now Pay Later (Simpl, LazyPay, etc.)

### Payment Gateways
- **Razorpay**: Primary payment gateway with full Indian payment ecosystem
- **Cashfree**: Fallback payment gateway for redundancy
- **Manual**: For COD payments

### Payment Status Flow
```
PENDING → PROCESSING → SUCCESS
                     ↓
                   FAILED
                     ↓
        REFUND_PENDING → REFUNDED
```

## API Endpoints

### Payment Operations
- `POST /v1/payments/initiate` - Initiate new payment
- `POST /v1/payments/verify` - Verify Razorpay payment
- `GET /v1/payments/{payment_id}` - Get payment details
- `GET /v1/payments/order/{order_id}` - Get payment by order ID
- `GET /v1/payments` - List payments with filters
- `POST /v1/payments/refund` - Initiate refund
- `GET /v1/payments/{payment_id}/logs` - Get payment activity logs

### Webhooks
- `POST /v1/payments/webhooks/razorpay` - Razorpay webhook handler
- `POST /v1/payments/webhooks/cashfree` - Cashfree webhook handler

## Setup

### Prerequisites
- Python 3.11+
- PostgreSQL 15+
- Redis 7+

### Installation

1. Create virtual environment:
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

2. Install dependencies:
```powershell
pip install -r requirements.txt
```

3. Configure environment variables:
```powershell
# Create .env file
DATABASE_URL=postgresql+asyncpg://localgrocery:dev_password_change_in_prod@localhost:5432/localgrocery
REDIS_URL=redis://:dev_password_change_in_prod@localhost:6379/0

# Razorpay credentials (sandbox)
RAZORPAY_KEY_ID=rzp_test_your_key_id
RAZORPAY_KEY_SECRET=your_key_secret
RAZORPAY_WEBHOOK_SECRET=your_webhook_secret

# Cashfree credentials (test)
CASHFREE_APP_ID=your_app_id
CASHFREE_SECRET_KEY=your_secret_key
CASHFREE_WEBHOOK_SECRET=your_webhook_secret

# Order Service URL
ORDER_SERVICE_URL=http://localhost:8003
```

### Database Migrations

The service will automatically create tables on startup. For production, use proper migrations.

## Running the Service

### Development
```powershell
cd backend\services\payment_service
uvicorn app.main:app --reload --port 8004
```

Access API documentation: http://localhost:8004/docs

### Testing
```powershell
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test
pytest tests/test_payments.py::test_initiate_payment_razorpay -v
```

## Architecture

### Database Models

#### Payment
- Core payment transaction record
- Stores gateway order ID, payment ID, signature
- Tracks payment status and refund details
- Contains JSONB fields for gateway responses and webhook attempts

#### PaymentLog
- Audit trail for all payment events
- Records status transitions, webhook events, errors
- Useful for debugging and compliance

### Service Integration

#### Order Service Integration
Payment Service updates order payment status via HTTP API:
- On payment success: Update order to `PAID`
- On refund completion: Update order to `REFUNDED`

#### Gateway Integration
- **Razorpay**: Create order, verify signature, handle webhooks
- **Cashfree**: Create payment session, handle callbacks
- **Idempotency**: Prevents duplicate payments using idempotency keys

### Security

#### Signature Verification
All payment gateway webhooks are verified using HMAC-SHA256 signatures to prevent tampering.

#### Idempotency
Payment initiation uses idempotency keys to prevent duplicate charges during retries.

#### Webhook Handling
- Validates webhook signatures
- Logs all webhook attempts
- Returns 200 OK to prevent retries for invalid payloads
- Processes events asynchronously

## Configuration

### Gateway Settings
- `RAZORPAY_ENVIRONMENT`: "sandbox" or "production"
- `CASHFREE_ENVIRONMENT`: "TEST" or "PROD"
- `PAYMENT_GATEWAY_TIMEOUT`: Request timeout in seconds (default: 30)

### Currency
- `DEFAULT_CURRENCY`: "INR" (Indian Rupee)

## Error Handling

### Common Error Codes
- `PAYMENT_GATEWAY_TIMEOUT`: Gateway request timed out (retry)
- `PAYMENT_DECLINED`: Card/UPI declined by gateway (no retry)
- `INVALID_SIGNATURE`: Webhook signature verification failed
- `PAYMENT_NOT_FOUND`: Payment ID or order ID not found
- `REFUND_EXCEEDS_AMOUNT`: Refund amount exceeds available amount
- `DUPLICATE_PAYMENT`: Payment already exists for order

## Monitoring

### Metrics to Track
- Payment success rate by gateway
- Payment processing latency
- Webhook processing time
- Refund completion rate
- Payment method distribution

### Logs to Monitor
- Payment creation events
- Signature verification failures
- Webhook processing errors
- Order service update failures
- Gateway API errors

## Development Notes

### Testing Payments
Use Razorpay/Cashfree test credentials and test cards for development.

### Webhook Testing
Use ngrok or similar to expose local endpoint for webhook delivery:
```powershell
ngrok http 8004
# Configure webhook URL in gateway dashboard
```

### Mock Implementations
Current implementation includes mock gateway integrations. Replace with actual SDK calls in production:
```python
# Replace mock with actual Razorpay SDK
import razorpay
client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
order = client.order.create({...})
```

## Production Deployment

### Environment Configuration
- Use production gateway credentials
- Enable webhook signature verification
- Set appropriate timeouts and retry logic
- Configure proper CORS origins
- Enable database connection pooling

### Monitoring & Alerting
- Set up alerts for payment failure rates >5%
- Monitor webhook processing latency
- Track refund success rates
- Alert on gateway timeout spikes

## API Response Format

All endpoints return standardized responses:

```json
{
  "success": true,
  "message": "Operation description",
  "data": {...},
  "error": null
}
```

## Related Services
- **Order Service** (port 8003): Receives payment status updates
- **Notification Service** (port 8005): Sends payment confirmation messages

## Support
For issues or questions, refer to project documentation in `/wiki/Backend/`.
