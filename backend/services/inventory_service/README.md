# Inventory Service

FastAPI-based real-time inventory management service for the LocalGrocery platform.

## Features

- **Real-time Stock Management**: Track inventory across multiple stores
- **Inventory Reservations**: Hold stock during checkout with configurable TTL
- **Redis Caching**: High-performance cache layer for inventory queries
- **Stock Audit Trail**: Immutable logging of all inventory operations
- **Concurrent Access**: Database row-level locking (SELECT ... FOR UPDATE) prevents overselling
- **Automatic Cleanup**: Background task expires old reservations
- **Low Stock Alerts**: Status transitions to track inventory health

## Tech Stack

- **FastAPI 0.104.1**: Async REST framework
- **SQLAlchemy 2.0.35 + asyncpg**: Async ORM with PostgreSQL
- **Redis 5.0.4**: In-memory cache for fast inventory lookups
- **APScheduler**: Background task scheduling
- **Pydantic 2.10.4**: Request/response validation

## Setup

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis 7+

### Installation

```bash
# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
# source venv/bin/activate    # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Update `.env` with your database and Redis URLs:

```
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/localgrocery
REDIS_URL=redis://:password@localhost:6379/0
RESERVATION_VALIDITY_MINUTES=15
ORDER_SERVICE_URL=http://localhost:8003
```

## Running

```bash
python -m uvicorn app.main:app --reload --port 8007
```

Access Swagger UI: `http://localhost:8007/docs`

## API Endpoints

### Inventory Management
- `POST /v1/inventory` - Create new product inventory
- `GET /v1/inventory/{store_id}/{product_id}` - Get inventory details
- `POST /v1/inventory/{store_id}/{product_id}/adjust` - Adjust stock (add/remove)

### Availability
- `POST /v1/inventory/check-availability` - Bulk availability check (for cart validation)

### Reservations (Checkout)
- `POST /v1/reservations` - Reserve inventory for order
- `POST /v1/reservations/{order_id}/confirm` - Confirm after payment
- `POST /v1/reservations/{order_id}/cancel` - Cancel and restore stock

### Audit
- `GET /v1/audit-logs/{inventory_id}` - Get stock change history

## Database Schema

### ProductInventory
Tracks real-time stock for each store-product combination.

```sql
CREATE TABLE product_inventory (
    id UUID PRIMARY KEY,
    store_id UUID NOT NULL,
    product_id UUID NOT NULL,
    stock_qty INTEGER NOT NULL,           -- Total stock
    reserved_qty INTEGER NOT NULL,         -- Held by active reservations
    available_qty INTEGER NOT NULL,        -- stock_qty - reserved_qty
    status ENUM(IN_STOCK, LOW_STOCK, OUT_OF_STOCK),
    reorder_level INTEGER,
    selling_price FLOAT,
    UNIQUE(store_id, product_id)
);
```

### InventoryReservation
Holds reservation details for checkout process (15-min TTL).

```sql
CREATE TABLE inventory_reservations (
    id UUID PRIMARY KEY,
    order_id UUID NOT NULL UNIQUE,
    customer_id UUID NOT NULL,
    items JSONB NOT NULL,              -- [{store_id, product_id, qty}]
    status ENUM(RESERVED, CONFIRMED, CANCELLED, EXPIRED),
    reserved_at TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,      -- 15 minutes from creation
    confirmed_at TIMESTAMP
);
```

### StockAuditLog
Immutable audit trail for compliance and debugging.

```sql
CREATE TABLE stock_audit_logs (
    id UUID PRIMARY KEY,
    inventory_id UUID NOT NULL,
    event_type ENUM(...),
    old_qty INTEGER,
    new_qty INTEGER,
    order_id UUID,
    source STRING,                      -- ORDER, MANUAL_ADJUSTMENT, DAMAGE, RETURN
    created_at TIMESTAMP
);
```

## Caching Strategy

Redis is used for high-performance reads:

```
inventory:{store_id}:{product_id} → {stock_qty, available_qty, status, ...}
  TTL: 60 minutes (configurable via REDIS_CACHE_TTL_MINUTES)
  Invalidated on: Stock adjustment, reservation changes
  
reservation:{order_id} → {status, expires_at, ...}
  TTL: 15 minutes (matches RESERVATION_VALIDITY_MINUTES)
```

## Key Algorithms

### Reservation (Checkout)

1. **Validate**: Check available_qty >= requested_qty for all items
2. **Lock**: Use `SELECT ... FOR UPDATE` to lock inventory rows
3. **Reserve**: Deduct from available_qty, increment reserved_qty
4. **Create Record**: InventoryReservation with 15-min expiry
5. **Cache**: Store in Redis for fast expiry checks
6. **Cleanup**: Background job expires reservations after TTL

### Confirmation (After Payment)

1. **Find**: Locate InventoryReservation by order_id
2. **Validate**: Check status = RESERVED
3. **Update**: Change status to CONFIRMED
4. **Lock**: Mark inventory as unavailable for further ops
5. **Notify**: Alert other services (Order, Notification) via HTTP

### Cancellation (Order Failure)

1. **Lock**: Acquire row locks on all inventory items
2. **Restore**: Increment available_qty, decrement reserved_qty
3. **Update**: Set reservation status = CANCELLED
4. **Cache Invalidate**: Remove from Redis
5. **Audit Log**: Record cancellation event with reason

## Testing

```bash
# Run all tests
pytest -v

# With coverage
pytest --cov=app

# Specific test
pytest tests/test_inventory.py::test_reserve_inventory_success -v
```

**Test Coverage**: 25+ test cases covering:
- Inventory creation & retrieval
- Stock adjustments
- Reservation lifecycle (reserve → confirm → cancel)
- Availability checks
- Audit logging
- Edge cases (duplicates, negative stock, insufficient qty)

## Monitoring & Alerts

### Metrics to Track
- Reservation confirmation rate (target: >95%)
- Cache hit rate (target: >80%)
- Reservation expiry rate (low = good checkout flow)
- Stock accuracy (periodic audit)

### Common Issues

**Oversold Stock**: If available_qty becomes negative
- Cause: Race condition in concurrent requests
- Fix: Ensure `SELECT ... FOR UPDATE` is always used

**Cache Stale Data**: If inventory not updated after sale
- Cause: Cache not invalidated on stock change
- Fix: Always call `invalidate_inventory_cache()` after updates

**Expired Reservations Not Cleaned**: If cleanup job fails
- Cause: APScheduler not running or database error
- Cause: Check scheduler logs, verify cleanup_expired_reservations() executes

## Integration Points

- **Order Service** (8003): Validates inventory before order confirmation
- **Payment Service** (8004): Triggers inventory confirmation after payment
- **Notification Service** (8006): Alerts on low stock
- **Cart Service**: Validates items in cart via check-availability endpoint

## Performance Targets

| Operation | Target | Current |
|-----------|--------|---------|
| Get Inventory (cached) | <10ms | ~5ms |
| Get Inventory (DB) | <50ms | ~30ms |
| Reserve Stock | <200ms | ~100ms |
| Confirm Reservation | <100ms | ~80ms |
| Cancel Reservation | <150ms | ~120ms |

## Future Enhancements

- [ ] Inventory synchronization with POS systems
- [ ] Demand forecasting for automatic reorders
- [ ] Warehouse management system (WMS) integration
- [ ] Real-time low stock notifications to retailers
- [ ] Inventory transfer between stores
- [ ] Batch expiry tracking and alerts
