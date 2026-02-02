# Delivery Service

Delivery partner management and order delivery tracking service for LocalGrocery platform.

## Features

- **Delivery Management**: Create and track deliveries for orders
- **Partner Assignment**: Auto or manual assignment of delivery partners
- **Real-time Tracking**: Location tracking throughout delivery lifecycle
- **Distance Calculation**: Accurate distance and ETA using geopy
- **Fee Calculation**: Dynamic delivery fees based on distance
- **Status Tracking**: Complete audit trail of delivery events

## API Endpoints

### Deliveries

- `POST /v1/deliveries` - Create delivery for order
- `POST /v1/deliveries/{id}/assign` - Assign to partner (auto/manual)
- `PATCH /v1/deliveries/{id}/status` - Update delivery status
- `GET /v1/deliveries/{id}` - Get delivery details
- `GET /v1/deliveries/order/{order_id}` - Get delivery by order
- `GET /v1/deliveries` - List deliveries (with filters)
- `GET /v1/deliveries/{id}/tracking` - Get tracking history

### Delivery Partners

- `GET /v1/partners/nearby` - Find nearby available partners
- `GET /v1/partners/{id}` - Get partner details
- `PATCH /v1/partners/{id}/location` - Update partner location
- `PATCH /v1/partners/{id}/status` - Update partner availability

## Delivery Status Flow

```
PENDING → ASSIGNED → PICKED_UP → IN_TRANSIT → DELIVERED
    ↓         ↓          ↓            ↓
CANCELLED CANCELLED  FAILED       FAILED
```

## Setup

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Docker Desktop (for local development)

### Installation

```powershell
# Navigate to service directory
cd backend\services\delivery_service

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Update DATABASE_URL and other settings
```

### Database Setup

The service automatically creates tables on startup. Ensure PostgreSQL is running:

```powershell
# Check if PostgreSQL is running (Docker)
docker ps | Select-String postgres

# If not running, start Docker Compose
cd ..\..\..\
docker-compose up -d postgres
```

### Run Service

```powershell
# Development mode (with auto-reload)
python -m uvicorn app.main:app --reload --port 8005

# Production mode
python -m uvicorn app.main:app --host 0.0.0.0 --port 8005
```

### Run Tests

```powershell
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test
pytest tests/test_deliveries.py::test_create_delivery -v

# Run with verbose output
pytest -v
```

## Configuration

Key settings in `app/config.py`:

```python
# Delivery parameters
MAX_DELIVERY_RADIUS_KM = 10.0  # Maximum delivery distance
DELIVERY_PARTNER_SEARCH_RADIUS_KM = 5.0  # Partner search radius
AVERAGE_SPEED_KMH = 20.0  # For ETA calculation

# Fee structure
BASE_DELIVERY_FEE = 20.0  # Base fee in ₹
PER_KM_FEE = 5.0  # Additional fee per km beyond 2km
```

## Database Schema

### deliveries

- `id` (UUID, PK)
- `order_id` (UUID, unique)
- `delivery_partner_id` (UUID, FK)
- `status` (enum: PENDING, ASSIGNED, etc.)
- `pickup_location` (JSONB)
- `delivery_location` (JSONB)
- `current_location` (JSONB)
- `distance_km` (Float)
- `estimated_time_minutes` (Float)
- `delivery_fee` (Decimal)
- Timestamps: `assigned_at`, `picked_up_at`, `in_transit_at`, `delivered_at`

### delivery_partners

- `id` (UUID, PK)
- `name`, `phone`, `email`
- `vehicle_type`, `vehicle_number`
- `status` (AVAILABLE, BUSY, OFFLINE)
- `current_location` (JSONB)
- `total_deliveries`, `successful_deliveries`
- `rating` (Float)
- `is_verified`, `is_active`

### delivery_tracking

- `id` (UUID, PK)
- `delivery_id` (UUID, FK)
- `event_type` (e.g., DELIVERY_CREATED, STATUS_UPDATE_PICKED_UP)
- `status_from`, `status_to`
- `location` (JSONB)
- `event_data` (JSONB)
- `triggered_by` (SYSTEM, PARTNER, CUSTOMER)

## Integration with Other Services

### Order Service

Updates order delivery status when delivery status changes:
- `PICKED_UP` → Order status: `OUT_FOR_DELIVERY`
- `DELIVERED` → Order status: `DELIVERED`
- `FAILED` → Order status: `DELIVERY_FAILED`

### Maps APIs

- **Google Maps / Mapbox**: Distance matrix, directions
- **geopy**: Distance calculations between coordinates

## Testing

Test coverage includes:
- ✅ Delivery creation with fee/ETA calculation
- ✅ Auto/manual partner assignment
- ✅ Status transition validation
- ✅ Real-time location tracking
- ✅ Partner search by proximity
- ✅ Distance and fee calculations
- ✅ Invalid status transition handling
- ✅ No available partners scenario

## API Documentation

Access interactive API docs at:
- Swagger UI: `http://localhost:8005/docs`
- ReDoc: `http://localhost:8005/redoc`

## Production Deployment

```powershell
# Build Docker image
docker build -t localgrocery/delivery-service:latest .

# Run container
docker run -d \
  -p 8005:8005 \
  -e DATABASE_URL=postgresql+asyncpg://... \
  -e REDIS_URL=redis://... \
  localgrocery/delivery-service:latest
```

## Troubleshooting

### Database connection error
```
Ensure PostgreSQL is running and DATABASE_URL is correct
Check: docker ps | Select-String postgres
```

### Import errors
```
Ensure virtual environment is activated
Check: pip list | Select-String fastapi
```

### Distance calculation errors
```
Verify location coordinates are valid (-90 to 90 for lat, -180 to 180 for lng)
Check geopy installation: pip show geopy
```

## License

Proprietary - LocalGrocery Platform
