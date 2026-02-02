# Order Service

FastAPI microservice for managing orders in LocalGrocery platform.

## Features

- ✅ Create orders with multiple items
- ✅ Order status lifecycle (PLACED → CONFIRMED → PACKED → OUT_FOR_DELIVERY → DELIVERED)
- ✅ Payment status tracking (PENDING → PAID/FAILED/REFUNDED)
- ✅ Order listing with filters and pagination
- ✅ Order cancellation
- ✅ Idempotency key support for webhook safety
- ✅ Comprehensive test suite

## Quick Start

### Setup

```bash
cd backend/services/order_service
python -m venv venv
# Windows:
.\venv\Scripts\Activate.ps1
# Linux/Mac:
source venv/bin/activate

pip install -r requirements.txt
```

### Database

```bash
# From root directory
cd scripts
.\migrate-postgres.ps1 up  # This creates order service tables
```

### Run Service

```bash
cd backend/services/order_service
uvicorn app.main:app --reload --port 8003
```

Visit `http://localhost:8003/docs` for Swagger UI.

### Run Tests

```bash
export DATABASE_URL="postgresql+asyncpg://localgrocery:dev_password_change_in_prod@localhost:5432/localgrocery"
export TEST_DATABASE_URL="postgresql+asyncpg://localgrocery:dev_password_change_in_prod@localhost:5432/localgrocery_test"
pytest -v
```

## API Endpoints

### Create Order
```
POST /api/v1/orders/
{
  "customer_id": "uuid",
  "store_id": "uuid",
  "payment_method": "UPI",
  "delivery_address": {
    "street": "123 Main St",
    "city": "Mumbai",
    "pincode": "400001"
  },
  "items": [
    {
      "product_id": "uuid",
      "product_name": "Rice",
      "quantity": 2,
      "unit_price": "100.00"
    }
  ]
}
```

### Get Order
```
GET /api/v1/orders/{order_id}
GET /api/v1/orders/number/{order_number}
```

### List Orders
```
GET /api/v1/orders/?customer_id=...&store_id=...&status=PLACED&page=1&page_size=20
```

### Update Order Status
```
PUT /api/v1/orders/{order_id}
{
  "status": "CONFIRMED"
}
```

### Cancel Order
```
DELETE /api/v1/orders/{order_id}
```

## Database Schema

### Orders Table
- `id`: UUID (PK)
- `customer_id`: UUID (FK to customers)
- `store_id`: UUID (FK to stores)
- `order_number`: String (unique, human-readable)
- `status`: Enum (PLACED, CONFIRMED, PACKED, OUT_FOR_DELIVERY, DELIVERED, CANCELLED)
- `payment_status`: Enum (PENDING, PAID, FAILED, REFUNDED)
- `subtotal, tax, delivery_fee, discount, total_amount`: Decimal pricing
- `delivery_address`: JSONB (address details)
- `idempotency_key`: String (for payment webhook safety)
- Timestamps: `created_at`, `updated_at`, `confirmed_at`, `delivered_at`

### OrderItems Table
- `id`: UUID (PK)
- `order_id`: UUID (FK to orders)
- `product_id`: UUID (product reference)
- `product_name, quantity, unit_price, total_price`: Line item details
- `variant_data`: JSONB (size, color, etc.)
- `status`: Enum (synchronized with parent order)

## Integration Points

### Auth Service
- Validates JWT token in request headers
- Extracts user ID from token claims

### Catalog Service
- Validates product IDs exist
- Fetches product names and pricing (future enhancement)

### Payment Service (future)
- Handles payment processing
- Updates order payment_status via webhook

### Delivery Service (future)
- Receives order confirmation
- Assigns driver and creates delivery

## Testing

19 tests covering:
- ✅ Order creation with validation
- ✅ Order retrieval (by ID and order number)
- ✅ Order listing with filters and pagination
- ✅ Status transitions (with validation)
- ✅ Order cancellation
- ✅ Edge cases (invalid address, no items, etc.)
