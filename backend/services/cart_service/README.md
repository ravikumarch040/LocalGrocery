# Cart Service

Shopping cart management microservice for LocalGrocery platform. Handles cart operations (create, read, update, delete), item management, and validation before checkout.

## Overview

The Cart Service provides a complete shopping cart solution with:
- ✅ Create/Read/Update/Delete cart operations
- ✅ Add/Remove/Update items in cart
- ✅ Multi-store cart support (cart items can be from different stores)
- ✅ Price and inventory validation
- ✅ Cart grouping by store (for order splitting)
- ✅ Cart expiration management

## Architecture

```
Cart Service (8008)
├── FastAPI application
├── PostgreSQL database (carts, cart_items tables)
├── Redis caching
└── Integration with:
    ├── Catalog Service (8002) - Price validation
    └── Inventory Service (8007) - Stock availability
```

## Database Schema

### carts table
```sql
CREATE TABLE carts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP,
    INDEX (customer_id)
);
```

### cart_items table
```sql
CREATE TABLE cart_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cart_id UUID NOT NULL REFERENCES carts(id),
    product_id VARCHAR(255) NOT NULL,
    store_id VARCHAR(255) NOT NULL,
    quantity INTEGER DEFAULT 1,
    unit_price FLOAT NOT NULL,
    product_name VARCHAR(500),
    product_image_url VARCHAR(500),
    is_price_valid BOOLEAN DEFAULT TRUE,
    is_in_stock BOOLEAN DEFAULT TRUE,
    validation_errors JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    INDEX (cart_id),
    INDEX (product_id),
    INDEX (store_id)
);
```

## API Endpoints

### Cart Operations
- `POST /v1/carts` - Create cart
- `GET /v1/carts/{cart_id}` - Get cart with items
- `GET /v1/carts/customer/{customer_id}` - Get customer's active cart
- `DELETE /v1/carts/{cart_id}` - Delete cart
- `POST /v1/carts/{cart_id}/clear` - Clear all items

### Cart Items
- `POST /v1/carts/{cart_id}/items` - Add item
- `POST /v1/carts/{cart_id}/items/bulk` - Add multiple items
- `PUT /v1/carts/{cart_id}/items/{item_id}` - Update quantity
- `DELETE /v1/carts/{cart_id}/items/{item_id}` - Remove item

### Validation & Checkout
- `POST /v1/carts/{cart_id}/validate` - Validate all items
- `POST /v1/carts/{cart_id}/checkout` - Prepare checkout

### Health
- `GET /health` - Service health check

## Setup & Installation

### Local Development

1. **Create virtual environment:**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

2. **Install dependencies:**
```powershell
pip install -r requirements.txt
```

3. **Configure environment:**
```powershell
# Copy and edit .env
cp .env.example .env
```

4. **Start PostgreSQL and Redis:**
```powershell
# Using Docker
docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=dev_password postgres:15
docker run -d -p 6379:6379 redis:latest
```

5. **Run service:**
```powershell
python -m uvicorn app.main:app --reload --port 8008
```

6. **Access documentation:**
- Swagger UI: http://localhost:8008/docs
- ReDoc: http://localhost:8008/redoc

## Running Tests

```powershell
# All tests
pytest

# Specific test file
pytest tests/conftest.py -v

# With coverage
pytest --cov=app

# Watch mode
pytest-watch
```

## Usage Examples

### Create Cart
```bash
curl -X POST http://localhost:8008/v1/carts \
  -H "Content-Type: application/json" \
  -d '{"customer_id": "cust_123"}'
```

### Add Item to Cart
```bash
curl -X POST http://localhost:8008/v1/carts/{cart_id}/items \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "prod_456",
    "store_id": "store_789",
    "quantity": 2,
    "unit_price": 100.0
  }'
```

### Get Cart
```bash
curl http://localhost:8008/v1/carts/{cart_id}
```

### Validate Cart
```bash
curl -X POST http://localhost:8008/v1/carts/{cart_id}/validate
```

### Prepare Checkout
```bash
curl -X POST http://localhost:8008/v1/carts/{cart_id}/checkout \
  -H "Content-Type: application/json" \
  -d '{
    "cart_id": "cart_123",
    "customer_id": "cust_123",
    "address_id": "addr_456"
  }'
```

## Key Features

### Multi-Store Support
- Cart items can be from different stores
- At checkout, cart is automatically split into one order per store
- Each order has separate delivery and billing

### Price Validation
- Validates product price hasn't changed by >5%
- Updates item flag if price changes
- Prevents customer from paying outdated price

### Inventory Validation
- Checks stock availability in Inventory Service
- Validates quantity requested is in stock
- Allows graceful degradation if Inventory Service unavailable

### Cart Expiration
- Carts expire after configurable period (default: 72 hours)
- Prevents stale carts from cluttering database
- Can be extended by customer activity

## Configuration

**Environment Variables:**

```
# Service
SERVICE_PORT=8008
DEBUG=True

# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/db
DB_POOL_SIZE=20

# Redis
REDIS_URL=redis://:password@localhost:6379/0

# Service URLs
CATALOG_SERVICE_URL=http://localhost:8002
INVENTORY_SERVICE_URL=http://localhost:8007
ORDER_SERVICE_URL=http://localhost:8003

# Cart Config
MAX_CART_ITEMS=100
MAX_QUANTITY_PER_ITEM=1000
CART_TTL_HOURS=72
```

## Development Notes

### Adding New Endpoints
1. Add route in `app/api_routes.py`
2. Add schema in `app/schemas.py` if needed
3. Add service logic in `app/services.py`
4. Add tests in `tests/conftest.py`

### Database Migrations
```powershell
# Create migration
alembic revision --autogenerate -m "Add new field"

# Run migration
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Service Integration
- **Calls:** Catalog (8002) and Inventory (8007) for validation
- **Called by:** Order Service (8003) at checkout
- **Events:** Publishes cart_validated, checkout_initiated events

## Performance Targets

| Metric | Target |
|--------|--------|
| Add item latency p95 | <100ms |
| Get cart latency p95 | <50ms |
| Validate cart latency p95 | <500ms |
| Cart size limit | 100 items |
| Availability target | 99.99% |

## Troubleshooting

### Cart Not Found
- Verify cart_id is correct UUID format
- Check cart hasn't expired
- Ensure customer_id matches

### Inventory Validation Fails
- Check Inventory Service (8007) is running
- Verify product_id exists in catalog
- Check store_id is correct

### Price Validation Fails
- Check Catalog Service (8002) is running
- Verify product price hasn't significantly changed
- Can retry adding item with updated price

## Related Services

- **Order Service (8003)** - Creates orders from cart checkout
- **Catalog Service (8002)** - Product metadata and pricing
- **Inventory Service (8007)** - Stock management and availability
- **Payment Service (8004)** - Payment processing after order
- **Notification Service (8006)** - Order confirmation notifications

## Next Steps

1. ✅ Cart Service implementation complete
2. 🔄 Integration tests (Order → Cart → Payment flow)
3. Load testing and performance tuning
4. Docker containerization
5. CI/CD pipeline integration
6. Production deployment
