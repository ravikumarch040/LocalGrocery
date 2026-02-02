# Microservices Integration Testing Guide

## Quick Testing

### 1. Health Checks
Verify all services are running:

```powershell
# Check Notification Service (currently running)
(Invoke-WebRequest -Uri "http://localhost:8006/health" -UseBasicParsing).Content

# Response:
# {"status":"healthy","service":"notification_service","version":"1.0.0"}
```

### 2. Order Flow Testing

#### Step 1: Create Order
```bash
curl -X POST http://localhost:8003/v1/orders \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "550e8400-e29b-41d4-a716-446655440000",
    "store_id": "550e8400-e29b-41d4-a716-446655440001",
    "items": [
      {
        "product_id": "550e8400-e29b-41d4-a716-446655440002",
        "quantity": 2,
        "price": 100
      }
    ]
  }'
```

#### Step 2: Initiate Payment
```bash
curl -X POST http://localhost:8004/v1/payments/initiate \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": "<order_id_from_step_1>",
    "amount": 200,
    "currency": "INR",
    "gateway": "razorpay",
    "customer_id": "550e8400-e29b-41d4-a716-446655440000"
  }'
```

#### Step 3: Create Delivery
```bash
curl -X POST http://localhost:8005/v1/deliveries \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": "<order_id_from_step_1>",
    "pickup_location": {
      "lat": 12.9716,
      "lng": 77.5946,
      "address": "Store Location"
    },
    "delivery_location": {
      "lat": 12.9352,
      "lng": 77.6245,
      "address": "Customer Location"
    }
  }'
```

#### Step 4: Send Notification
```bash
curl -X POST http://localhost:8006/v1/notifications \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "notification_type": "ORDER_STATUS",
    "channel": "SMS",
    "message": "Your order has been confirmed!"
  }'
```

## Unit Testing

### Run All Tests
```powershell
# Order Service
cd backend\services\order_service
pytest -v
pytest --cov=app --cov-report=html

# Payment Service
cd backend\services\payment_service
pytest -v
pytest --cov=app --cov-report=html

# Delivery Service
cd backend\services\delivery_service
pytest -v
pytest --cov=app --cov-report=html

# Notification Service
cd backend\services\notification_service
pytest -v
pytest --cov=app --cov-report=html
```

### Run Specific Test
```powershell
cd backend\services\order_service
pytest tests/test_orders.py::test_create_order -v
```

### Test with Coverage Report
```powershell
pytest --cov=app --cov-report=term-missing --cov-report=html
# HTML report: htmlcov/index.html
```

## Integration Testing

### Complete Order-to-Delivery Flow
```powershell
# 1. Start all services
.\start-all-services.ps1

# 2. Run integration tests (from root directory)
pytest tests/integration/test_order_flow.py -v

# 3. Monitor database
psql -h localhost -U localgrocery -d localgrocery
  SELECT * FROM orders ORDER BY created_at DESC LIMIT 5;
  SELECT * FROM payments ORDER BY created_at DESC LIMIT 5;
  SELECT * FROM deliveries ORDER BY created_at DESC LIMIT 5;
```

### Load Testing (1000 concurrent orders)
```powershell
# Using k6
k6 run tests/load/order_creation.js --vus 1000 --duration 5m

# Results:
# - Target: <200ms p95 latency
# - Success rate: >99%
# - Error rate: <0.1%
```

## Troubleshooting

### Service Won't Start
```powershell
# Check if port is in use
netstat -ano | Select-String "8005"

# Kill process on port
Get-Process | Where-Object {$_.Name -eq "python"} | Stop-Process -Force

# Restart service
cd backend\services\delivery_service
python -m uvicorn app.main:app --reload --port 8005
```

### Database Connection Issues
```powershell
# Check PostgreSQL is running
docker ps | Select-String postgres

# If not running, start Docker Compose
cd backend
docker-compose up -d postgres

# Verify database exists
psql -h localhost -U localgrocery -d postgres -c "\l"
```

### Payment Webhook Testing
```bash
# Simulate Razorpay webhook
curl -X POST http://localhost:8004/v1/webhooks/razorpay \
  -H "Content-Type: application/json" \
  -H "X-Razorpay-Signature: <signature>" \
  -d '{
    "event": "payment.authorized",
    "payload": {
      "payment": {
        "entity": {
          "id": "pay_xxx",
          "status": "authorized"
        }
      }
    }
  }'
```

## Monitoring & Debugging

### View Service Logs
```powershell
# Order Service logs (from service window)
# Logs show request/response details

# Check database logs
docker logs localgrocery-postgres

# View Redis cache
redis-cli
  KEYS *
  GET notification:user:550e8400-e29b-41d4-a716-446655440000
```

### Performance Metrics
```powershell
# Response time tracking
# Available in Grafana (once monitoring setup)
# Query examples:
# - Average order creation time
# - Payment processing latency
# - Delivery assignment duration
# - Notification delivery success rate
```

### Database Queries for Testing
```sql
-- Check all orders
SELECT * FROM orders ORDER BY created_at DESC LIMIT 10;

-- Check order items
SELECT oi.* FROM order_items oi
JOIN orders o ON oi.order_id = o.id
ORDER BY oi.created_at DESC LIMIT 10;

-- Check payments
SELECT * FROM payments ORDER BY created_at DESC LIMIT 10;

-- Check deliveries
SELECT * FROM deliveries ORDER BY created_at DESC LIMIT 10;

-- Check notifications
SELECT * FROM notifications ORDER BY created_at DESC LIMIT 10;

-- Order status flow
SELECT order_id, status, created_at FROM order_tracking
WHERE order_id = '<order_id>'
ORDER BY created_at;

-- Payment flow
SELECT order_id, status, gateway, created_at FROM payment_logs
WHERE order_id = '<order_id>'
ORDER BY created_at;
```

## Success Criteria

✅ All services start without errors  
✅ Health endpoints respond with 200 OK  
✅ Order creation completes in <200ms  
✅ Payment processing completes in <500ms  
✅ Delivery assignment completes in <100ms  
✅ Notifications sent within 5 seconds  
✅ All tests pass (>95% coverage)  
✅ No SQL injection vulnerabilities  
✅ Proper error handling and logging  
✅ Database transactions are ACID compliant  

---

## Next Testing Phase

1. **Mobile App Integration** - Test with Flutter apps
2. **Stress Testing** - 5000+ concurrent users
3. **Failure Recovery** - Database failover, service restart
4. **Security Testing** - Penetration testing, API security
5. **Performance Tuning** - Query optimization, caching strategy
