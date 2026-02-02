# LocalGrocery Backend - Python + FastAPI

**Stack**: Python 3.11+ | FastAPI | SQLAlchemy 2.0 | Pydantic | Uvicorn

**MVP Architecture**: PostgreSQL (transactional + JSONB catalog + FTS) + Redis (cache) + Outbox Pattern (events)

This is the backend for the LocalGrocery hyperlocal grocery marketplace. Uses Python + FastAPI for rapid development, superior validation, and excellent Copilot support.

> **📘 Note**: This follows the **MVP Stack Migration** plan. We use PostgreSQL for everything (transactional data + product catalog via JSONB + full-text search), Redis for caching, and the Outbox pattern for async events. This simplifies development while supporting <10K SKUs and <1000 events/sec. See `wiki/MVP_STACK_MIGRATION.md` for scaling strategy.

## 🚀 Quick Start

### Prerequisites
- Python 3.11+ ([download](https://www.python.org/downloads/))
- Docker & Docker Compose
- PostgreSQL client (optional)

### 1. Setup Infrastructure (MVP Stack)

```powershell
# Start MVP services (PostgreSQL, Redis, PgBouncer)
docker-compose -f docker-compose.dev.yml up -d

# Verify services
docker ps
redis-cli ping  # Redis health check
psql -h localhost -U localgrocery -c "SELECT version()"  # PostgreSQL health check
```

### 2. Setup Python Environment

```powershell
# Create virtual environment
python -m venv venv

# Activate (Windows)
.\venv\Scripts\Activate.ps1

# Activate (Linux/Mac)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Initialize Database

```powershell
# Run PostgreSQL migrations (includes FTS indexes + Outbox table)
cd scripts
.\migrate-postgres.ps1 up

# Verify FTS and Outbox setup
$env:PGPASSWORD='dev_password_change_in_prod'
psql -h localhost -U localgrocery -d localgrocery -c "\d products"
psql -h localhost -U localgrocery -d localgrocery -c "\d outbox_events"
```

### 4. Run Services

```powershell
# Auth Service (example)
cd services/auth_service
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8001

# Visit Swagger UI: http://localhost:8001/docs
```

---

## 📁 Service Structure

```
services/
├── auth_service/                  # Authentication & JWT
├── catalog_service/               # Product catalog
├── inventory_service/             # Stock management
├── cart_service/                  # Shopping cart
├── order_service/                 # Order lifecycle
├── payment_service/               # Payment processing
└── notification_service/          # FCM + SMS
```

Each service has its own:
- `app/` - FastAPI application
- `tests/` - pytest test suite
- `requirements.txt` - Dependencies
- `Dockerfile` - Container image
- `README.md` - Service documentation

---

## 🛠️ Development Workflow

### Create New Service

```powershell
mkdir services\my_service
cd services\my_service

# Create structure
mkdir app\api\v1\{endpoints,schemas}
mkdir app\{models,crud,services,utils}
mkdir tests

# Copy from template (see PYTHON_SETUP_GUIDE.md)
```

### Run Tests

```powershell
cd services\auth_service

# All tests
pytest

# With coverage
pytest --cov=app

# Specific test
pytest tests/test_auth.py::test_send_otp -v

# Watch mode
pytest-watch tests/
```

### Format Code

```powershell
# Format with Black
black app/

# Sort imports
isort app/

# Type checking
mypy app/
```

---

## 🔗 Database Connection

### PostgreSQL (Primary Database)

```powershell
# From Python
# DATABASE_URL = "postgresql+asyncpg://localgrocery:password@localhost:5432/localgrocery"

# Direct connection
$env:PGPASSWORD='dev_password_change_in_prod'
psql -h localhost -U localgrocery -d localgrocery

# List tables
\dt

# Run query
SELECT * FROM users;

# Full-Text Search example
SELECT name, category FROM products 
WHERE search_vector @@ to_tsquery('rice & basmati');

# Query product variants (JSONB)
SELECT name, variants->'sizes' FROM products 
WHERE variants @> '{"sizes": ["1kg"]}';
```

### Redis (Cache & Sessions)

```powershell
# From Python
# REDIS_URL = "redis://:password@localhost:6379/0"

# Direct connection
redis-cli -a dev_password_change_in_prod

# Check keys
KEYS *

# Get value
GET cart:user_123
```

---

## 🐳 Docker

### Build Service Image

```powershell
cd services\auth_service

# Build
docker build -t localgrocery-auth:v1.0.0 .

# Run
docker run -p 8001:8000 \
docker run -p 8001:8001 \
    -e DATABASE_URL="postgresql+asyncpg://..." \
    localgrocery-auth:v1.0.0
```

### Example Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ app/
COPY tests/ tests/

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 📚 API Documentation

### Automatic Docs

Once service is running:

- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc
- **OpenAPI JSON**: http://localhost:8001/openapi.json

### Example Endpoint

```python
from fastapi import APIRouter, Depends
from app.schemas import UserResponse
from app.services import UserService

router = APIRouter()

@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: str) -> UserResponse:
    """Get user by ID."""
    user = await UserService().get_user(user_id)
    return user
```

---

## 🔐 Environment Variables

Copy and edit `.env.local`:

```bash
# App
NODE_ENV=development
PORT=8001

# Database (PostgreSQL for all data)
DATABASE_URL=postgresql+asyncpg://localgrocery:password@localhost:5432/localgrocery

# Redis (Cache & Sessions)
REDIS_URL=redis://:password@localhost:6379/0

# Outbox Pattern (Event Processing)
OUTBOX_POLL_INTERVAL_SECONDS=5  # How often to poll outbox_events table
OUTBOX_BATCH_SIZE=100           # Max events to process per batch

# JWT
JWT_SECRET=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Payments (Dual Gateway)
RAZORPAY_KEY_ID=your_key
RAZORPAY_KEY_SECRET=your_secret
CASHFREE_APP_ID=your_app_id
CASHFREE_SECRET_KEY=your_secret

# SMS & OTP
MSG91_AUTH_KEY=your_key
OTP_EXPIRY_MINUTES=10
OTP_MAX_ATTEMPTS=3

# Firebase (Push Notifications)
FCM_SERVER_KEY=your_key
```

---

## � Outbox Pattern (Async Events)

Instead of Kafka, we use the **Outbox Pattern** for async event processing:

### How It Works

1. **Write Events**: Services write events to `outbox_events` table in same transaction
2. **Poll Events**: APScheduler job polls table every 5 seconds
3. **Process Events**: Unprocessed events are consumed and marked as processed
4. **Cleanup**: Processed events archived/deleted after 30 days

### Example: Publishing Event

```python
# app/services/order.py
from app.models import OutboxEvent

async def create_order(self, order_data: OrderCreate) -> Order:
    async with self.db.begin():
        # Create order
        order = Order(**order_data.dict())
        self.db.add(order)
        
        # Publish event to outbox
        event = OutboxEvent(
            event_type="order.created",
            aggregate_id=order.id,
            payload={"order_id": str(order.id), "customer_id": str(order.customer_id)}
        )
        self.db.add(event)
        
        # Both committed together
        await self.db.flush()
    
    return order
```

### Example: Consuming Events

```python
# app/consumers/outbox_processor.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler

class OutboxProcessor:
    async def process_events(self):
        # Fetch unprocessed events
        events = await self.db.execute(
            select(OutboxEvent)
            .where(OutboxEvent.processed == False)
            .limit(100)
            .with_for_update(skip_locked=True)
        )
        
        for event in events.scalars():
            # Route to appropriate handler
            if event.event_type == "order.created":
                await self.handle_order_created(event.payload)
            elif event.event_type == "payment.success":
                await self.handle_payment_success(event.payload)
            
            # Mark as processed
            event.processed = True
            event.processed_at = datetime.utcnow()
        
        await self.db.commit()

# In app/main.py
scheduler = AsyncIOScheduler()
scheduler.add_job(
    OutboxProcessor().process_events,
    'interval',
    seconds=5,  # Poll every 5 seconds
    id='outbox_processor'
)
scheduler.start()
```

### When to Upgrade to Kafka

- Event volume >1000/sec consistently
- Need complex event routing (topics, partitions)
- Require event replay capabilities
- Multiple external consumers

---

## �📖 Detailed Guides

- [Python Setup Guide](PYTHON_SETUP_GUIDE.md) - Complete Python & FastAPI setup
- [Service Structure](PYTHON_SETUP_GUIDE.md#📁-service-structure-template) - How to organize services
- [Tech Stack Analysis](../TECH_STACK_ANALYSIS.md) - Why Python + FastAPI

---

## 🚨 Troubleshooting

### Import Errors

```powershell
# Verify venv is activated
python -c "import sys; print(sys.prefix)"

# Reinstall requirements
pip install --force-reinstall -r requirements.txt
```

### Async Test Issues

```powershell
# Make sure pytest-asyncio is installed
pip install pytest-asyncio

# Add to conftest.py:
pytest_plugins = ('pytest_asyncio',)
```

### Port Already in Use

```powershell
# Find and kill process using port
lsof -i :8001  # Linux/Mac
netstat -ano | findstr :8001  # Windows

# Or use different port
python -m uvicorn app.main:app --port 8002
```

---

## ✅ Next Steps

1. ✅ Infrastructure running
2. ✅ Python environment setup
3. ⏳ Implement Auth Service (see PYTHON_SETUP_GUIDE.md)
4. ⏳ Build remaining services
5. ⏳ Create Flutter apps

---

**Built with FastAPI for clean, fast, and maintainable code** 🚀
