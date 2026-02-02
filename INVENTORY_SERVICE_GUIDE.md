# LocalGrocery - Inventory Service (Port 8007)

## Status: ✅ OPERATIONAL

**Service Health**: Healthy  
**Port**: 8007  
**Version**: 1.0.0  
**Tech Stack**: FastAPI 0.104.1, SQLAlchemy 2.0.35, asyncpg 0.31.0, Redis 5.0.4, APScheduler

---

## Quick Start

### Access API
- **Swagger UI**: http://localhost:8007/docs
- **Health Check**: http://localhost:8007/health

### Example Requests

```bash
# Create inventory
curl -X POST http://localhost:8007/v1/inventory \
  -H "Content-Type: application/json" \
  -d '{
    "store_id": "550e8400-e29b-41d4-a716-446655440000",
    "product_id": "550e8400-e29b-41d4-a716-446655440001",
    "stock_qty": 100,
    "cost_price": 50.0,
    "selling_price": 100.0
  }'

# Check availability
curl -X POST http://localhost:8007/v1/inventory/check-availability \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      {"store_id": "...", "product_id": "...", "qty": 50}
    ]
  }'

# Reserve inventory (during checkout)
curl -X POST http://localhost:8007/v1/reservations \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": "order-123",
    "customer_id": "cust-456",
    "items": [
      {"store_id": "...", "product_id": "...", "qty": 30}
    ]
  }'

# Confirm reservation (after payment success)
curl -X POST http://localhost:8007/v1/reservations/{order_id}/confirm \
  -H "Content-Type: application/json" \
  -d '{"reason": "Payment successful"}'

# Cancel reservation (if order fails)
curl -X POST http://localhost:8007/v1/reservations/{order_id}/cancel \
  -H "Content-Type: application/json" \
  -d '{"reason": "User cancelled"}'
```

---

## Key Features

### 1. Real-Time Stock Management
- Track inventory for each store-product combination
- Real-time available quantity calculation (stock_qty - reserved_qty)
- Automatic status tracking (IN_STOCK, LOW_STOCK, OUT_OF_STOCK)

### 2. Inventory Reservations
- Hold stock during checkout (15-minute default TTL)
- Concurrent reservation support with row-level locking (SELECT...FOR UPDATE)
- Automatic cleanup of expired reservations (APScheduler)

### 3. Redis Caching
- Fast inventory lookups (<10ms from cache)
- Cache invalidation on stock changes
- TTL-based cache expiry (60 minutes configurable)

### 4. Immutable Audit Trail
- Every stock change logged to `stock_audit_logs` table
- Event types: STOCK_ADDED, STOCK_REMOVED, STOCK_RESERVED, STOCK_CONFIRMED, etc.
- Full context captured: order_id, user_id, source, reason

### 5. Stock Adjustment Support
- Manual stock counts
- Return processing
- Damage/loss records
- Custom notes and metadata

---

## Core Concepts

### Available Quantity Calculation
```
available_qty = stock_qty - reserved_qty
```

### Reservation Flow

**Step 1: Reserve (Checkout)**
- Validates availability
- Locks inventory rows
- Deducts from available_qty
- Creates InventoryReservation record (expires in 15 mins)
- Caches reservation for fast expiry checks

**Step 2: Confirm (Payment Success)**
- Finds reservation by order_id
- Updates status to CONFIRMED
- Logs confirmation event
- Invalidates cache

**Step 3: Cancel (Order Failure)**
- Restores available_qty (adds back reserved amount)
- Updates status to CANCELLED
- Logs cancellation with reason
- Purges from cache

---

## Database Schema

### ProductInventory Table
```sql
CREATE TABLE product_inventory (
    id UUID PRIMARY KEY,
    store_id UUID NOT NULL,
    product_id UUID NOT NULL,
    stock_qty INTEGER NOT NULL,          -- Total stock
    reserved_qty INTEGER NOT NULL,       -- Held by reservations
    available_qty INTEGER NOT NULL,      -- stock - reserved
    cost_price FLOAT,
    selling_price FLOAT,
    status ENUM(IN_STOCK, LOW_STOCK, OUT_OF_STOCK),
    reorder_level INTEGER,
    supplier_id UUID,
    batch_number VARCHAR,
    expiry_date TIMESTAMP,
    product_metadata JSONB,              -- SKU, barcode, etc.
    last_stock_check TIMESTAMP,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    UNIQUE(store_id, product_id)
);
```

### InventoryReservation Table
```sql
CREATE TABLE inventory_reservations (
    id UUID PRIMARY KEY,
    order_id UUID NOT NULL UNIQUE,
    customer_id UUID NOT NULL,
    items JSONB NOT NULL,                -- [{store_id, product_id, qty, inventory_id}]
    status ENUM(RESERVED, CONFIRMED, CANCELLED, EXPIRED),
    reserved_at TIMESTAMP,
    confirmed_at TIMESTAMP,
    expires_at TIMESTAMP,
    cancelled_at TIMESTAMP,
    reason VARCHAR,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

### StockAuditLog Table
```sql
CREATE TABLE stock_audit_logs (
    id UUID PRIMARY KEY,
    inventory_id UUID NOT NULL,
    event_type ENUM(...),
    old_qty INTEGER,
    new_qty INTEGER,
    qty_changed INTEGER,                 -- old - new
    order_id UUID,
    user_id UUID,
    source VARCHAR,                      -- ORDER, MANUAL_ADJUSTMENT, DAMAGE, RETURN
    notes TEXT,
    extra_data JSONB,
    created_at TIMESTAMP
);
```

---

## Caching Strategy

### Inventory Cache
```
Key: inventory:{store_id}:{product_id}
Value: {stock_qty, available_qty, reserved_qty, status, selling_price, ...}
TTL: 60 minutes (configurable via REDIS_CACHE_TTL_MINUTES)
Invalidation: On any stock change
```

### Reservation Cache
```
Key: reservation:{order_id}
Value: {id, status, expires_at}
TTL: 15 minutes (matches RESERVATION_VALIDITY_MINUTES)
Invalidation: On confirmation or cancellation
```

---

## API Endpoints (13 Total)

### Inventory Management
| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/v1/inventory` | Create new inventory |
| GET | `/v1/inventory/{store_id}/{product_id}` | Get inventory details |
| POST | `/v1/inventory/{store_id}/{product_id}/adjust` | Adjust stock (add/remove) |

### Availability Checking
| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/v1/inventory/check-availability` | Bulk check items for cart |

### Reservations
| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/v1/reservations` | Reserve inventory for order |
| POST | `/v1/reservations/{order_id}/confirm` | Confirm after payment |
| POST | `/v1/reservations/{order_id}/cancel` | Cancel and restore stock |

### Audit & Monitoring
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/v1/audit-logs/{inventory_id}` | Get stock change history |
| GET | `/health` | Service health check |

---

## Configuration

### Environment Variables

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/localgrocery

# Redis
REDIS_URL=redis://:password@localhost:6379/0

# Inventory
RESERVATION_VALIDITY_MINUTES=15          # Cart hold duration
LOW_STOCK_THRESHOLD_PERCENT=0.20         # Alert if stock < 20% of reorder_level
STOCK_CLEANUP_INTERVAL_MINUTES=5         # Cleanup task frequency

# Service URLs (for inter-service communication)
ORDER_SERVICE_URL=http://localhost:8003
NOTIFICATION_SERVICE_URL=http://localhost:8006
```

---

## Integration Points

### Order Service (Port 8003)
- **Before Order Confirmation**: Call `POST /v1/inventory/check-availability`
- **After Order Creation**: Call `POST /v1/reservations` to hold stock
- **After Payment**: Call `POST /v1/reservations/{order_id}/confirm`
- **On Order Failure**: Call `POST /v1/reservations/{order_id}/cancel`

### Notification Service (Port 8006)
- **Triggered by**: Low stock status changes
- **Alert Types**: LOW_STOCK_ALERT, OUT_OF_STOCK_ALERT
- **Recipients**: Store owners (retailers)

### Cart Service (Port 8005 - Future)
- **Availability Check**: Before adding items to cart
- **Cache Integration**: Invalidates on inventory updates

---

## Background Tasks

### Reservation Cleanup Job
- **Frequency**: Every 5 minutes (configurable)
- **Action**: Finds expired reservations and cancels them
- **Updates**: InventoryReservation.status = EXPIRED
- **Restores**: Stock is returned to available_qty

---

## Performance Characteristics

| Operation | Latency | Notes |
|-----------|---------|-------|
| Get Inventory (cached) | <10ms | Redis hit |
| Get Inventory (DB) | <50ms | PostgreSQL query |
| Check Availability | <100ms | Bulk query |
| Reserve Stock | <200ms | Includes row locking |
| Confirm Reservation | <100ms | Single update |
| Cancel Reservation | <150ms | Restores multiple items |

---

## Testing

### Run Tests
```bash
cd inventory_service
.\venv\Scripts\Activate.ps1
pytest -v
```

### Test Coverage
- 25+ comprehensive test cases
- Unit tests for each operation
- Integration tests for workflows
- Edge case coverage (race conditions, negative stock, etc.)

### Example Test Commands
```bash
# All tests
pytest tests/test_inventory.py -v

# Specific test
pytest tests/test_inventory.py::test_reserve_inventory_success -v

# With coverage report
pytest --cov=app tests/test_inventory.py
```

---

## Common Workflows

### 1. Complete Order Checkout
```
1. GET /v1/inventory/check-availability    ← Validate items exist
2. POST /v1/reservations                   ← Reserve stock
3. [Payment Processing]
4. POST /v1/reservations/{orderId}/confirm ← Lock inventory
5. POST to Order Service                   ← Create order
```

### 2. Order Cancellation
```
1. POST /v1/reservations/{orderId}/cancel  ← Restore stock
2. Update OrderService status              ← Mark order failed
3. POST to Notification Service            ← Refund notification
```

### 3. Stock Adjustment (Retailer)
```
1. POST /v1/inventory/{storeId}/{productId}/adjust
   - qty_change: positive (add) or negative (remove)
   - source: MANUAL_ADJUSTMENT, DAMAGE, RETURN, etc.
2. GET /v1/audit-logs/{inventoryId}       ← Verify change
```

---

## Monitoring & Alerts

### Key Metrics
- **Reservation Confirmation Rate**: >95% (orders successfully paid)
- **Cache Hit Rate**: >80% (fast inventory reads)
- **Stock Accuracy**: Audit trail reconciliation
- **Expiry Rate**: <5% (users completing checkout)

### Alert Conditions
- Availability query latency >500ms
- Redis disconnection
- Expired reservation queue size >1000
- Stock going negative (data corruption indicator)

---

## Common Issues & Solutions

### Problem: Oversold Stock
**Cause**: Race condition when multiple orders reserve same stock  
**Solution**: Always use `SELECT ... FOR UPDATE` for inventory updates  
**Verification**: Check audit logs for stock_qty going negative

### Problem: Cache Showing Stale Stock
**Cause**: Cache not invalidated after stock change  
**Solution**: Call `invalidate_inventory_cache()` after every update  
**Verification**: Compare Redis vs Database values

### Problem: Reservations Not Expiring
**Cause**: APScheduler not running or database error  
**Solution**: Check scheduler logs in service output  
**Manual Fix**: Run `cleanup_expired_reservations()` manually

### Problem: High Latency on Check-Availability
**Cause**: Too many items in bulk request or Redis slow  
**Solution**: Limit request to <50 items, check Redis memory usage  
**Optimization**: Use pagination for large catalogs

---

## Future Enhancements

- [ ] Batch inventory sync with POS systems
- [ ] Demand forecasting for auto-reorders
- [ ] Warehouse management system (WMS) integration
- [ ] Inventory transfer between stores
- [ ] Real-time low stock notifications
- [ ] Batch expiry tracking and alerts
- [ ] Supplier SKU mapping

---

## Related Services

- **Order Service** (8003): Consumes reservation endpoints
- **Payment Service** (8004): Triggers confirmation after payment
- **Delivery Service** (8005): Reads confirmed inventory for fulfillment
- **Notification Service** (8006): Sends low stock alerts
- **Catalog Service** (8002): Product metadata source

---

## Support

- **Swagger UI**: http://localhost:8007/docs
- **Health Check**: http://localhost:8007/health
- **Database**: PostgreSQL localgrocery DB
- **Cache**: Redis database 0
- **Logs**: Service console output
