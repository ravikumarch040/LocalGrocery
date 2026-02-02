# LocalGrocery Services - Quick Reference

## Service Inventory

| # | Service | Port | Status | Tests | Notes |
|---|---------|------|--------|-------|-------|
| 1 | Auth Service | 8001 | ⏳ Setup | ⏳ Pending | JWT + OTP (foundational) |
| 2 | Cart Service | 8005 | ⏳ Setup | ⏳ Pending | Multi-store cart validation |
| 3 | Catalog Service | 8002 | ✅ Done | ✅ 5/5 | Store + product metadata |
| 4 | Delivery Service | 8007 | ⏳ Setup | ⏳ Pending | Route optimization + ETA |
| 5 | Inventory Service | 8004 | ✅ Done | ✅ 18/18 + 8/8 | Stock + reservation mgmt |
| 6 | Notification Service | 8008 | ⏳ Setup | ⏳ Pending | FCM + SMS + Email |
| 7 | Order Service | 8003 | ✅ Done | ✅ 9/9 | Order lifecycle + settlement |
| 8 | Payment Service | 8006 | ⚠️ Fix | ⚠️ 14/15 | Razorpay + Cashfree dual |

## Running Tests

### Option 1: Master Script (Recommended)
```bash
# All services
cd backend
python run_all_tests.py

# Single service
python run_all_tests.py --service inventory

# Export results
python run_all_tests.py --output results.json

# Without auto-starting services
python run_all_tests.py --no-auto-start
```

### Option 2: Individual Service Tests
```bash
# Start service (in separate terminal)
cd backend/services/inventory_service
python -m uvicorn app.main:app --host 0.0.0.0 --port 8004

# In another terminal, run tests
python -m pytest tests/ -v                 # Unit tests
python test_inventory_apis.py              # Integration tests
```

### Option 3: Docker Compose (Full Stack)
```bash
# Start all services + dependencies
cd backend
docker-compose -f docker-compose.dev.yml up -d

# Run master test script
python run_all_tests.py
```

## Service Dependencies

```
Auth Service (8001)
    ↓
    Used by: All other services for JWT validation

Catalog Service (8002) + Inventory Service (8004)
    ↓
    Used by: Cart Service (8005)

Cart Service (8005) + Payment Service (8006)
    ↓
    Used by: Order Service (8003)

Order Service (8003)
    ↓
    Used by: Delivery Service (8007)

Notification Service (8008)
    ↓
    Used by: All services for event notifications
```

## Test Status Legend

- ✅ **Ready**: All tests passing (100%)
- ⚠️ **Mostly Ready**: >90% tests passing, needs fixes
- 🔄 **In Progress**: Tests being developed
- ⏳ **Pending**: Not yet started
- ❌ **Failing**: Critical issues, <90% passing

## Quick Troubleshooting

### Service won't start
```bash
# Check port is free
netstat -ano | findstr :8004

# Check logs
tail -f backend/services/inventory_service/service_*.log

# Kill stuck process
Get-Process python | Stop-Process -Force
```

### Tests timing out
```bash
# Increase timeout in run_all_tests.py
# Or run tests individually with more time
python -m pytest tests/ -v --timeout=300
```

### Database connection issues
```bash
# Verify PostgreSQL is running
psql -h localhost -U localgrocery -d localgrocery

# Check test DB exists
psql -h localhost -U localgrocery -l | grep localgrocery_test

# Create test DB if missing
createdb -h localhost -U localgrocery localgrocery_test
```

## Performance Targets

| Service | Latency p95 | Success Rate | Availability |
|---------|------------|--------------|--------------|
| Auth | <100ms | 99.99% | 99.99% |
| Cart | <200ms | 99.5% | 99.95% |
| Catalog | <300ms | 99.9% | 99.95% |
| Delivery | <500ms | 99% | 99.9% |
| Inventory | <50ms (cache) | 99.9% | 99.99% |
| Notification | <1s | 95% | 99.5% |
| Order | <200ms | 99.5% | 99.95% |
| Payment | <500ms | 98% | 99.9% |

## Important Files

```
/backend/
  ├── run_all_tests.py          # Master test runner
  ├── requirements.txt            # All dependencies
  ├── docker-compose.dev.yml      # Local dev environment
  └── services/
      ├── auth_service/
      ├── cart_service/
      ├── catalog_service/
      │   ├── tests/test_*.py    # Unit tests
      │   └── test_*_apis.py     # Integration tests
      ├── delivery_service/
      ├── inventory_service/
      │   ├── tests/test_*.py    # 18 unit tests ✅
      │   ├── test_inventory_apis.py  # 8 integration tests ✅
      │   └── app/
      │       ├── main.py
      │       ├── models/
      │       ├── api/v1/endpoints/
      │       └── services/
      ├── notification_service/
      ├── order_service/
      └── payment_service/
```

## Next Steps

1. **This Week**:
   - Fix Payment Service (1 failing test)
   - Implement Auth Service tests

2. **Next Week**:
   - Complete Cart Service tests
   - Begin Delivery Service tests

3. **By Feb 10**:
   - All services at ≥90% test coverage
   - Master script fully operational
   - CI/CD integration complete

## Contact & Support

- **Test Issues**: Check TEST_PLAN.md for detailed test matrix
- **Service Issues**: See individual service README.md
- **DB Issues**: See backend/PYTHON_SETUP_GUIDE.md
- **Architecture**: See wiki/Architecture/ directory
