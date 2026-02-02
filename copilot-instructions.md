# Copilot Instructions for LocalGrocery Platform

## Project Overview
**LocalGrocery** is a hyperlocal grocery marketplace platform empowering local retailers (kirana stores) in India through a multi-vendor mobile-first architecture. Three primary Flutter apps (Customer, Retailer, Delivery Partner) connect to a microservices backend.

### Key Mission
Enable local retailers to sell online competitively while delivering fast, trusted grocery experiences to customers in Tier-2/3 Indian cities.

### ⚠️ CRITICAL: Tech Stack Transition in Progress
**Current State (Jan 2026)**: Full-scale stack planned but MVP-optimized implementation underway:
- **Backend**: Python 3.11 + FastAPI + Uvicorn (✅ Confirmed)
- **Primary DB**: PostgreSQL with async support (asyncpg) (✅ In requirements.txt)
- **Infrastructure**: Still includes MongoDB, Kafka, Elasticsearch in requirements but MVP migration documented
- **MVP Plan**: Simplify to PostgreSQL FTS + Outbox pattern (see `wiki/MVP_STACK_MIGRATION.md`)

**When building new features**: Follow MVP patterns (PostgreSQL-only, sync over async for simplicity) unless discussing scale-up architecture.

---

## Architecture Essentials

### The Big Picture: Multi-Layer System
1. **Flutter Mobile Apps** (3 separate apps) → **API Gateway (REST/JWT)** → **Microservices** → **Data Layer**
2. **Event-Driven Backbone**: Currently Kafka planned; MVP uses Outbox pattern + APScheduler
3. **Data: Dual-Database Pattern (Planned) vs MVP (PostgreSQL-only)**
   - **PostgreSQL**: Transactional data (orders, payments, settlements, wallets, users) + JSONB for product variants
   - **MongoDB**: Planned for product catalog; MVP uses PostgreSQL JSONB instead
   - **Redis**: Cart, inventory cache, sessions (✅ Active)
   - **Elasticsearch**: Planned for search; MVP uses PostgreSQL Full-Text Search (FTS)

### Critical Data Flow Example (MVP Implementation)
```
Customer places order → Order Service (Postgres) → Write to outbox_events table
  → APScheduler polls outbox → Inventory Service reserves stock (via Redis + Postgres row lock)
  → Payment Service charges (Razorpay/Cashfree)
  → On success, write payment success to outbox
  → Delivery Service schedules (via route optimizer)
  → Driver updates status → settlement flows to retailer
```

**Key Difference from Original Plan**: Using database-based Outbox pattern instead of Kafka for <1000 events/sec workload.

### Core Microservices (in order of criticality)
1. **Auth Service** (JWT + OTP) — gateway to all user access
2. **Order Service** — heart of commerce (order lifecycle: PLACED→CONFIRMED→PACKED→OUT_FOR_DELIVERY→DELIVERED)
3. **Payment Service** — dual-gateway integration (Razorpay + Cashfree fallback)
4. **Inventory Service** — real-time stock management with reservations
5. **Catalog Service** — product/store metadata; coordinates with Elasticsearch
6. **Cart Service** — multi-store cart with price validation
7. **Delivery Service** — route optimization + rider assignment
8. **Notification Service** — FCM (push) + MSG91 (SMS/OTP)
9. **Wallet/Settlement Service** — ledger for customer points + retailer payouts

---

## Stack & Key Tech Choices

| Layer | Tech | Why |
|-------|------|-----|
| **Mobile** | Flutter (Dart) + Riverpod/Bloc | Single codebase, excellent on low-end devices, offline caching |
| **Backend** | Python 3.11 + FastAPI + Uvicorn | Excellent async support, superior validation (Pydantic), auto API docs, Copilot-friendly, ML-ready |
| **Backend ORM** | SQLAlchemy 2.0 + asyncpg | Type-safe, async support, excellent code review experience |
| **Primary DB** | PostgreSQL (RDS/Aurora) | ACID guarantees for financial data (orders, payments, settlements) |
| **Product Metadata** | PostgreSQL JSONB (MVP) / MongoDB (Scale-up) | MVP: JSONB for <10K SKUs; Scale: MongoDB for variant explosion |
| **Search** | PostgreSQL FTS (MVP) / Elasticsearch (Scale-up) | MVP: Built-in Full-Text Search; Scale: Geo-aware faceted filtering |
| **Cache & Queue** | Redis (ElastiCache) | Cart, inventory hot-path, sessions, distributed locks |
| **Events** | Outbox + APScheduler (MVP) / Kafka (Scale-up) | MVP: <1000 events/sec; Scale: High-throughput async workflows |
| **API Gateway** | Kong (open) or AWS API Gateway | Auth, rate-limiting, WAF, request routing |
| **Payments** | Razorpay + Cashfree (dual) | Full Indian payment ecosystem (UPI, wallets, cards, BNPL, instant payouts) |
| **Maps & Routing** | Mapbox/Google Maps + GraphHopper | Directions, distance matrix, vehicle routing optimization (VRP) |
| **Push/SMS** | FCM + MSG91 | Cross-platform push, India-specific SMS provider |
| **Cloud** | AWS (EKS, RDS, S3, Lambda) | Kubernetes orchestration, managed services; GCP/Azure viable |
| **IaC & CI/CD** | Terraform + GitHub Actions | Reproducible infra, image registry (ECR), staged environments |
| **Observability** | Prometheus + Grafana + ELK/OpenSearch + Sentry | Metrics, logs, traces, error tracking |

---

## Project Conventions & Patterns

### API Design
- **Protocol**: REST + JSON + JWT Bearer auth
- **Versioning**: Prefix routes (`/v1/...`)
- **Response Format**: All endpoints return `{ success, message, data?, error? }`
- **Error Codes**: Consistent HTTP status + business error codes in response
- **OpenAPI Contract**: Defined in `/backend/openapi.yaml` (Swagger UI ready)

### Database Naming
- PostgreSQL tables: snake_case, plural (`users`, `order_items`, `payment_gateways`)
- MongoDB collections: lowercase, plural (`products`, `product_variants`)
- All tables have `id` (UUID), `created_at`, `updated_at`

### Microservice Communication
- **Sync**: HTTP REST for immediate responses (checkout, inventory check)
- **Async (MVP)**: Outbox pattern (outbox_events table) polled by APScheduler for order lifecycle, inventory events
- **Async (Scale-up)**: Kafka topics when event volume >1000/sec or need complex event routing
- **Caching**: Redis for hot-paths (product catalog, store inventory, user sessions)
- **Idempotency Keys**: Critical for payment webhooks and order placement to handle retries safely

### Mobile App Structure (Flutter)
- **Navigation**: Independent stacks per BottomNav tab (Home, Orders, Wallet, Profile for Customer)
- **State Management**: Riverpod/Bloc for predictable state
- **Local Caching**: SQLite/Hive for offline-first retailer inventory
- **Deep Linking**: Ready for external promotions/order shares
- **Role-Based UI**: Same codebase, conditional rendering (CUSTOMER/RETAILER/DRIVER/ADMIN roles)

### Retailer KYC Flow (Trust & Compliance)
- **Step 1-3**: Basic info + business type + document upload (PAN, GST, bank)
- **Step 4**: Auto-verify GST via API, admin manual review
- **Step 5**: Commission assignment, store goes live, test order enabled
- **Key**: All retailers must pass KYC before accepting real orders

### Order Lifecycle States
```
PLACED → CONFIRMED (retailer accepts)
      → PACKED (retailer packs)
      → OUT_FOR_DELIVERY (driver picks up)
      → DELIVERED
      ↓ (alternatively)
      → CANCELLED
```
Payment status is independent: PENDING → PAID → (on refund) REFUNDED

### Settlement & Payout Logic
- Retailer earns: `order_total × (1 - commission_percent) - platform_fee`
- Held in retailer's settlement ledger
- Automated payouts via Cashfree Payouts or RazorpayX (daily/weekly, configured per retailer)

---

## Critical Integration Points

### Razorpay / Cashfree Payments
- **Always dual-gateway**: If Razorpay fails, retry with Cashfree
- **Webhook Validation**: Verify signature on payment status updates
- **Tokenization**: Store card/UPI tokens for one-tap checkout (no card data in your servers)
- **Settlements**: Use gateway settlement APIs for retailer payouts, not manual transfers

### Maps & Route Optimization
- **Google Maps / Mapbox**: Distance Matrix for ETA, Directions for navigation
- **GraphHopper**: Explicit route optimization for delivery batching (VRP solver)
- **Geo-Proximity Search**: Elasticsearch geo-queries for "find nearby stores within 5km"

### Firebase Cloud Messaging (FCM)
- **Device Registration**: Collect FCM tokens at app startup
- **Topics**: Subscribe users to topics like `order_status_${orderId}`, `store_${storeId}_new_orders`
- **Payload**: Keep under 4KB; link to deep-links for app navigation

### Kafka Event Topics (Critical for Async)
- `order.created` → inventory reserve, payment charge, delivery assign
- `payment.success` → unlock inventory, notify retailer + customer
- `inventory.reserved` → cache invalidation, real-time UI updates
- `order.shipped` → trigger rider tracking, customer notification

**MVP Alternative**: For MVP development, use Outbox pattern instead:
```sql
-- Outbox table structure
CREATE TABLE outbox_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type VARCHAR(100) NOT NULL,
    aggregate_id UUID NOT NULL,
    payload JSONB NOT NULL,
    processed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- APScheduler polls this table every 1-5 seconds
-- Processes unprocessed events and marks as processed
```

---

## Development Workflows

### Local Development
1. **Backend**: Docker Compose for PostgreSQL, MongoDB, Redis, Kafka, Elasticsearch
2. **API Testing**: Postman with collections per service; OpenAPI YAML imports directly
3. **Mobile**: Flutter emulator (Android) or simulator (iOS); mock auth with test tokens
4. **Environment**: `.env` files (dev/staging/prod) with feature flags

### Python Development Setup
```powershell
# Setup virtual environment (ALWAYS do this first)
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
# source venv/bin/activate    # Linux/Mac

# Install all dependencies
pip install -r requirements.txt

# Run a service
cd services\auth_service
python -m uvicorn app.main:app --reload --port 8001

# Access Swagger UI: http://localhost:8001/docs
```

### Key Commands Reference
```powershell
# Database migrations (PostgreSQL)
cd scripts
.\migrate-postgres.ps1 up      # Apply migrations
.\migrate-postgres.ps1 down    # Rollback last migration

# Run tests
pytest                          # All tests
pytest --cov=app               # With coverage
pytest -v tests/test_auth.py   # Specific test file

# Code formatting
black app/                      # Format code
isort app/                      # Sort imports
mypy app/                       # Type checking

# Database connections (PowerShell)
$env:PGPASSWORD='dev_password_change_in_prod'
psql -h localhost -U localgrocery -d localgrocery

redis-cli -a dev_password_change_in_prod

docker exec -it localgrocery-mongodb mongosh -u localgrocery -p dev_password_change_in_prod
```

### Build & Deployment Stages
1. **Dev**: Auto-deploy on every merge to `main`; manual promotions to staging/prod
2. **Staging**: Full integration tests; UAT by product/support team; payment gateways in sandbox
3. **Production**: Blue-green deployments; Kubernetes rolling updates; instant rollback on critical errors
4. **Database Migrations**: Handled via service-specific migration tools; backward-compatible schema changes

### Testing Strategy
- **Unit**: Logic in services (payment validation, inventory calculations)
- **Integration**: Cart → Order → Payment flow; Kafka event propagation
- **E2E**: Critical journeys (login → search → checkout → order tracking)
- **Mobile**: Focus on auth, cart accuracy, offline fallback
- **Load**: Simulate peak orders/second; identify bottlenecks in payment/order service

---

## Common Pitfalls & Solutions

### Inventory Oversell
- **Problem**: Race condition when multiple orders reserve same stock simultaneously
- **Solution**: Use Postgres `SELECT ... FOR UPDATE` for stock reservation within transaction
- **Cache Invalidation**: After each reservation, refresh inventory in Redis

### Payment Webhook Race Condition
- **Problem**: Webhook delivered twice; order marked as paid twice
- **Solution**: Use idempotency keys; check if payment already recorded before updating order status

### Order Split Across Stores
- **Problem**: Customer adds items from Store A + Store B; need two separate orders & deliveries
- **Solution**: Cart service pre-validates store eligibility; at checkout, auto-split into separate order records with shared parent order ID

### Delivery Latency
- **Problem**: Driver assigned late; customer sees long ETA
- **Solution**: Use Kafka batch processing + route optimizer; assign in <200ms after order payment

### Regional Language Support
- **Mobile**: Use Flutter's `intl` package; backend returns lang_code in user profile
- **Search**: Elasticsearch supports Hindi/regional languages with custom analyzers

---

## Code Example Patterns

### Microservice Boilerplate (Python + FastAPI)

#### Service Layer
```python
# app/services/order.py
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Order
from app.schemas import OrderCreate

class OrderService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_order(self, customer_id: str, items: list) -> Order:
        # 1. Validate inventory (call inventory service or Redis)
        # 2. Create order in DB with status PLACED
        order = Order(customer_id=customer_id, status="PLACED")
        self.db.add(order)
        await self.db.commit()
        # 3. Publish order.created event to Kafka
        await self.kafka_producer.send("order.created", order)
   python
# app/services/inventory.py
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

class InventoryService:
    async def reserve_stock(
        self,
        store_id: str,
        product_id: str,
        quantity: int,
    Pydantic Validation (Request/Response)
```python
# app/schemas/order.py
from pydantic import BaseModel, Field, field_validator
from typing import List
from datetime import datetime

class OrderItem(BaseModel):
    product_id: str = Field(..., min_length=1)
    quantity: int = Field(..., gt=0, le=1000)
    price: float = Field(..., gt=0)

class OrderCreate(BaseModel):
    customer_id: str = Field(..., min_length=1)
    store_id: str = Field(..., min_length=1)
    items: List[OrderItem] = Field(..., min_items=1)
    
    @field_validator('items')
    @classmethod
    def validate_items(cls, v):
        if not v:
            raise ValueError('At least one item required')
        return v

class OrderResponse(BaseModel):
    id: str
    customer_id: str
    status: str
    total_amount: float
    created_at: datetime
    items: List[OrderItem]
    
    class Config:
        from_attributes = True  # Enable Pydantic v2 ORM mode
```

### Inventory Reservation (Postgres + Redis)
```python
# app/services/inventory.py
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

class InventoryService:
    async def reserve_stock(
        self,
        store_id: str,
        product_id: str,
        quantity: int,
        db: AsyncSession,
        redis_client
    ) -> bool:
        # Reserve stock within transaction
        async with db.begin_nested():
            # Lock row for update
            stmt = select(Inventory).where(
                (Inventory.store_id == store_id) &
                (Inventory.product_id == product_id)
            ).with_for_update()
            
            inventory = await db.scalar(stmt)
            
            if inventory.stock_qty < quantity:
                raise InsufficientStockError()
            
            # Deduct stock
            inventory.stock_qty -= quantity
            await db.flush()
        
        # Invalidate cache
        cache_key = f"inventory:{store_id}:{product_id}"
        await redis_client.delete(cache_key)
        
        return True
```

```sql
-- Reserve stock (within transaction)
BEGIN;
SELECT stock_qty FROM inventory WHERE store_id = ? AND product_id = ? FOR UPDATE;
UPDATE inventory SET stock_qty = stock_qty - ?, updated_at = NOW() WHERE ...;
COMMIT;

-- Invalidate Redis cache
DEL inventory:${storeId}:${productId}
```

### FastAPI Endpoint Pattern
```python
# app/api/v1/endpoints/orders.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.services import OrderService
from app.schemas import OrderCreate, OrderResponse

router = APIRouter()

@router.post("/orders", response_model=OrderResponse)
async def create_order(
    order_create: OrderCreate,
    db: AsyncSession = Depends(get_db)
) -> OrderResponse:
    service = OrderService(db)
    order = await service.create_order(
        order_create.customer_id,
        order_create.items
    )
    return order
```

### Event Consumer (Kafka)
```python
# app/consumers/payment_consumer.py
from aiokafka import AIOKafkaConsumer
import asyncio

class PaymentConsumer:
    async def consume_payment_events(self):
        consumer = AIOKafkaConsumer(
            'payment.success',
            bootstrap_servers='localhost:9092',
            group_id='payment-consumer-group'
        )
        async with consumer:
            async for message in consumer:
                event = json.loads(message.value)
                # Process payment success event
                await self.handle_payment_success(event)
```

### Deep Link Handling (Flutter)
```dart
// In router.dart
RouteMatch deepLinkRoute = RouteMatch.match(
  uri: Uri.parse('app://order/12345'),
  routes: appRoutes,
);
// Automatically navigates to OrderTrackingScreen for order #12345
```

---

## File Structure Overview
```
LocalGrocery/
├── backend/
│   └── openapi.yaml          # Full API spec (Swagger/Postman ready)
├── wiki/
│   ├── Design_and_Architecture.md
│   ├── Database_Schema.md
│   ├── Implementation_Roadmap.md
│   ├── Retailer Onboarding & KYC Flow.md
│   ├── Architecture/           # Detailed architecture docs
│   ├── Backend/                # API contracts, DB schema details
│   ├── Mobile/                 # App flows (customer, retailer, delivery)
│   ├── FLUTTER WIREFRAMES/     # UI mockups
│   └── Product/                # Vision, roadmap, business model
├── .github/
│   └── copilot-instructions.md (this file)
```

---

## Build & Deployment Commands

### Local Development Setup
```bash
# Backend services (Docker Compose)
docker-compose -f docker-compose.dev.yml up -d

# Includes: PostgreSQL, MongoDB, Redis, Kafka, Elasticsearch, Zookeeper
# Verify: curl http://localhost:9200 (Elasticsearch)
#         redis-cli ping (Redis)
#         pg_isready -h localhost (Postgres)

# Environment file
cp .env.example .env.local
# Update: DB credentials, API keys (Razorpay test, MSG91 test)
```

### Backend Service Deployment
```bash
# Build Docker image (per service)
docker build -t localgrocery/order-service:v1.0.0 .

# Push to ECR (AWS)
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
docker tag localgrocery/order-service:v1.0.0 <account-id>.dkr.ecr.us-east-1.amazonaws.com/localgrocery/order-service:v1.0.0
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/localgrocery/order-service:v1.0.0

# Deploy to Kubernetes (EKS)
kubectl apply -f k8s/order-service-deployment.yaml --namespace=production
kubectl rollout status deployment/order-service -n production

# Rollback (if issues)
kubectl rollout undo deployment/order-service -n production
```

### Flutter Mobile Build
```bash
# Android APK (debug)
flutter build apk --debug

# Android App Bundle (release)
flutter build appbundle --release

# iOS IPA (release)
flutter build ios --release
# Then use Xcode to upload to App Store

# Web (for admin dashboard)
flutter build web --release
```

### Database Migrations
```bash
# PostgreSQL (using Flyway or custom scripts)
./scripts/migrate-postgres.sh up   # Apply migrations
./scripts/migrate-postgres.sh down # Rollback

# MongoDB (index creation)
db.products.createIndex({ "name": "text", "category": 1 })
db.products.createIndex({ "location": "2dsphere" })  # Geo-index

# Redis (no schema, but verify cache keys)
redis-cli KEYS "inventory:*" | wc -l
```

### CI/CD Pipeline (GitHub Actions)
```yaml
# .github/workflows/backend-ci.yml
on: [push, pull_request]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run tests
        run: npm test
      - name: Build Docker image
        run: docker build -t order-service .
      - name: Push to ECR
        run: |
          aws ecr get-login-password | docker login ...
          docker push ...
```

---

## API Error Codes & Responses

### Standard Error Response Format
```json
{
  "success": false,
  "message": "Payment gateway timeout",
  "error": {
    "code": "PAYMENT_GATEWAY_TIMEOUT",
    "httpStatus": 504,
    "details": {
      "gateway": "razorpay",
      "attemptedAt": "2026-01-17T10:30:00Z",
      "retryable": true
    }
  }
}
```

### Common Error Codes

| Code | HTTP | Scenario | Retry? |
|------|------|----------|--------|
| `AUTH_INVALID_OTP` | 401 | OTP mismatch or expired | No |
| `AUTH_TOKEN_EXPIRED` | 401 | JWT expired, need refresh | Yes |
| `RETAILER_KYC_PENDING` | 403 | Store not approved yet | No |
| `INVENTORY_OVERSOLD` | 409 | Stock unavailable | Yes |
| `CART_PRICE_CHANGED` | 409 | Price updated since add | No |
| `PAYMENT_GATEWAY_TIMEOUT` | 504 | Razorpay/Cashfree slow | Yes |
| `PAYMENT_DECLINED` | 402 | Card declined by gateway | No |
| `ORDER_NOT_FOUND` | 404 | Order ID invalid | No |
| `STORE_OUTSIDE_DELIVERY_RADIUS` | 422 | Customer location too far | No |
| `DELIVERY_PARTNER_UNAVAILABLE` | 503 | No drivers online | Yes |
| `WEBHOOK_SIGNATURE_INVALID` | 401 | Payment webhook tampering | No |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests | Yes |
| `DATABASE_TIMEOUT` | 500 | DB query stalled | Yes |

### Idempotency for Safe Retries
```typescript
// Payment endpoint example
POST /v1/payments/initiate
Headers:
  - Idempotency-Key: ${orderId}-${timestamp}
  
// Backend: Check if payment with same key exists
const existingPayment = await paymentRepo.findByIdempotencyKey(key);
if (existingPayment) {
  return existingPayment; // Avoid duplicate charge
}
```

---

## Testing Strategy

### Unit Tests (Per Service)
```typescript
// order.service.spec.ts
describe('OrderService', () => {
  it('should reserve inventory before confirming order', async () => {
    const order = await service.createOrder(customerId, items);
    expect(order.status).toBe('PLACED');
    
    // Verify inventory was reserved
    const reserved = await inventoryService.checkReservation(items[0].productId);
    expect(reserved).toBe(true);
  });

  it('should reject order if inventory insufficient', async () => {
    await expect(
      service.createOrder(customerId, tooManyItems)
    ).rejects.toThrow('INVENTORY_OVERSOLD');
  });
});
```

### Integration Tests (Service-to-Service)
```typescript
// order-payment-inventory.integration.spec.ts
describe('Order → Payment → Inventory Flow', () => {
  it('should emit payment.success event after successful charge', async (done) => {
    const order = await orderService.createOrder(customerId, items);
    
    await paymentService.chargeRazorpay(order.id, amount);
    
    // Listen for event
    eventBus.on('payment.success', (event) => {
      expect(event.orderId).toBe(order.id);
      expect(event.status).toBe('PAID');
      done();
    });
  });

  it('should unlock inventory on payment failure', async () => {
    // Mock Razorpay failure
    jest.spyOn(razorpayClient, 'charge').mockRejectedValue(new Error('Declined'));
    
    await expect(paymentService.chargeRazorpay(orderId, amount)).rejects.toThrow();
    
    // Verify inventory released
    const reserved = await inventoryService.checkReservation(productId);
    expect(reserved).toBe(false);
  });
});
```

### E2E Tests (Critical User Journeys)
```typescript
// customer-checkout.e2e.spec.ts
describe('Customer Checkout Flow', () => {
  it('should complete full order from login to confirmation', async () => {
    // 1. Login
    const { token } = await client.post('/auth/otp/verify', { phone, otp });
    
    // 2. Search & add to cart
    const products = await client.get('/search?q=rice');
    await client.post('/cart/add', { productId: products[0].id, quantity: 2 }, { headers: { Authorization: `Bearer ${token}` } });
    
    // 3. Checkout
    const order = await client.post('/orders', { 
      addressId, paymentMethod: 'UPI' 
    }, { headers: { Authorization: `Bearer ${token}` } });
    
    expect(order.status).toBe('PLACED');
    expect(order.paymentStatus).toBe('PENDING');
    
    // 4. Verify retailer sees order
    const retailerOrders = await retailerClient.get('/orders', { 
      headers: { Authorization: `Bearer ${retailerToken}` } 
    });
    expect(retailerOrders.some(o => o.id === order.id)).toBe(true);
  });
});
```

### Mobile E2E Tests (Flutter)
```dart
// test/e2e/checkout_flow_test.dart
void main() {
  group('Customer Checkout Flow', () {
    testWidgets('Complete order from home to tracking', (tester) async {
      await tester.pumpWidget(const MyApp());
      
      // Login
      await tester.enterText(find.byType(TextField), '9876543210');
      await tester.tap(find.byText('Send OTP'));
      await tester.pumpAndSettle();
      
      // Search
      await tester.enterText(find.byType(SearchBar), 'rice');
      await tester.tap(find.text('Add to Cart'));
      
      // Checkout
      await tester.tap(find.byText('Proceed to Checkout'));
      await tester.pumpAndSettle();
      
      // Order placed
      expect(find.text('Order Confirmed'), findsOneWidget);
    });
  });
}
```

### Load Testing (Peak Orders/Second)
```bash
# Using Apache JMeter or k6
k6 run --vus 1000 --duration 5m load-test.js

# Scenario: 1000 concurrent users placing orders
# Target: <200ms p95 latency, <0.1% error rate
# Monitor: Payment timeout, inventory lock contention
```

---

## Security Checklist

### Authentication & Authorization
- [ ] JWT tokens: 15-min expiry for access, 7-day refresh token
- [ ] OTP: 6-digit, valid for 10 minutes, rate-limited (max 3 attempts/hour)
- [ ] Refresh token rotation: New refresh token issued on each use
- [ ] RBAC: Role-based access enforced at API Gateway (CUSTOMER, RETAILER, DRIVER, ADMIN)
- [ ] Rate limiting: 100 req/min per user, 10 req/min per IP for auth endpoints

### Payment Security
- [ ] **Never store card/UPI data**: Use gateway tokenization (Razorpay hosted checkout or token vault)
- [ ] Webhook signature validation: All Razorpay/Cashfree webhooks verified via HMAC-SHA256
- [ ] Idempotency keys: Prevent duplicate charges from webhook retries
- [ ] PCI DSS scope: Keep card handling in PCI-compliant gateway, not in servers
- [ ] Card encryption: TLS 1.3+ for all payment flows

### Data Protection
- [ ] Database encryption: Enable Postgres SSL connections, RDS encryption at rest
- [ ] Secrets management: AWS Secrets Manager or HashiCorp Vault (no hardcoded keys)
- [ ] Sensitive fields: Hash retailer GST numbers, mask customer phone in logs
- [ ] GDPR/data retention: Delete customer data after 12 months (unless legal hold)

### Infrastructure Security
- [ ] API Gateway WAF: Enable AWS WAF for SQL injection, XSS, bot detection
- [ ] DDoS protection: Cloudflare or AWS Shield
- [ ] Kubernetes network policies: Restrict inter-service traffic to defined routes
- [ ] Database backups: Encrypted, tested restore weekly, replicated cross-region
- [ ] VPN/private networks: Services communicate over private VPCs, no public endpoints

### Compliance
- [ ] KYC for retailers: PAN, GST, bank verification before store goes live
- [ ] GST compliance: Generate e-invoices, maintain audit logs, file returns
- [ ] NPCI guidelines: Comply with UPI transaction limits, fraud reporting
- [ ] Audit logs: Record all financial transactions, admin actions, data access
- [ ] Data residency: Store Indian customer data in AWS India region

---

## Migration Guides

### Adding a New Microservice
1. **Create service directory** under `/backend/services/`
2. **Copy from template**: NestJS boilerplate (auth, logging, error handling)
3. **Database**: Create migration file in `/db/migrations/`
4. **API routes**: Define in OpenAPI spec (`/backend/openapi.yaml`)
5. **Kafka events**: Register topics in event schema
6. **Deployment**: Add K8s manifest in `/k8s/` and CI/CD step in GitHub Actions
7. **Documentation**: Update architecture diagram and wiki

### Scaling Database (PostgreSQL)
```sql
-- Add read replicas for read-heavy queries (catalog, search)
-- Use connection pooling (PgBouncer) to reduce connection overhead
-- Partition large tables by date (orders by created_at)

-- Example: Partition orders table
CREATE TABLE orders_2026_q1 PARTITION OF orders
  FOR VALUES FROM ('2026-01-01') TO ('2026-04-01');

-- Archive old partitions for long-term storage (S3)
```

### Migrating from Single Store to Multi-Store Cart
```typescript
// 1. Schema change: Add store_id to cart_items
ALTER TABLE cart_items ADD COLUMN store_id UUID;

// 2. Backfill existing carts (assume single store per user)
UPDATE cart_items SET store_id = ? WHERE cart_id = ?;

// 3. Add validation: Reject adding items from different stores to same cart
// 4. Add auto-split: At checkout, split into separate orders per store
// 5. Update mobile app: Show store-wise grouping in cart UI
```

### Switching Payment Gateway (Razorpay → Cashfree)
```typescript
// 1. Dual-gateway mode: Try Razorpay first, fallback to Cashfree
async chargePayment(orderId, amount) {
  try {
    return await razorpay.charge(orderId, amount);
  } catch (error) {
    if (error.retryable) {
      return await cashfree.charge(orderId, amount);
    }
    throw error;
  }
}

// 2. Webhook routing: Route callbacks to correct gateway handler
// 3. Settlement reconciliation: Use both APIs to verify payouts
// 4. Gradual migration: Route 10% → 50% → 100% to new gateway
```

---

## Performance Targets & Monitoring

### Service Level Objectives (SLOs)

| Service | Metric | Target | Alert Threshold |
|---------|--------|--------|-----------------|
| **Auth Service** | Latency p95 | <100ms | >150ms |
| **Auth Service** | Availability | 99.99% | <99.95% |
| **Order Service** | Latency p95 | <200ms | >300ms |
| **Order Service** | Success rate | >99.5% | <99% |
| **Payment Service** | Latency p95 | <500ms | >750ms (includes gateway) |
| **Payment Service** | Charge success | >98% | <95% |
| **Inventory Service** | Latency p99 | <50ms | >75ms (Redis hit) |
| **Search Service** | Latency p95 | <300ms | >500ms |
| **Checkout (E2E)** | Duration | <5s | >8s |
| **Mobile App** | Crash rate | <0.1% | >0.5% |

### Monitoring Stack

```bash
# Metrics (Prometheus + Grafana)
- Request latency distribution (p50, p95, p99)
- Error rates by service and endpoint
- Payment gateway success/failure rates
- Inventory lock contention
- Kafka lag (consumer lag monitoring)
- Database query time (slow query log)
- Redis memory usage and evictions

# Logs (ELK / OpenSearch)
- Structured logging: service, request_id, user_id, timestamp, level
- Payment transactions: include order_id, gateway, amount, status
- Errors: stack trace, context, user impact
- Retention: 7 days hot, 90 days archive

# Tracing (Jaeger)
- Trace order placement: Auth → Cart → Order → Payment → Inventory
- Identify slow hops (e.g., inventory service calling external API)
```

### Key Dashboards
1. **Business Dashboard**: GMV, orders/day, top stores, customer acquisition
2. **Operational Dashboard**: Active orders, delivery ETAs, failed payments, pending KYC
3. **Technical Dashboard**: Service latencies, error rates, Kafka lag, DB connections
4. **Incident Dashboard**: Real-time alerts, on-call rotation, runbooks

### Alerting Rules
```yaml
# Prometheus alert rules
- name: HighOrderFailureRate
  expr: rate(orders_failed_total[5m]) > 0.005
  for: 5m
  severity: critical
  action: Page on-call engineer

- name: PaymentGatewayTimeout
  expr: rate(payment_gateway_timeout_total[5m]) > 0.01
  for: 2m
  severity: warning
  action: Send Slack notification

- name: InventoryLockContention
  expr: histogram_quantile(0.95, inventory_lock_wait_ms) > 1000
  for: 10m
  severity: warning
  action: Review checkout load
```

---

## Quick Debugging Checklist

- **Order stuck in PENDING payment**: Check Razorpay webhook logs; look for idempotency key conflicts
- **Inventory oversold**: Verify Redis cache consistency with DB; check for missing `FOR UPDATE` locks
- **Slow search**: Profile Elasticsearch query; check index refresh interval; verify geo-filters are narrowing results
- **Delivery delays**: Check route optimizer batch size; measure Kafka event lag
- **Mobile app crashes on checkout**: Verify JWT token expiry; check payment gateway timeout config
- **High latency on /catalog/products**: Check Elasticsearch cluster health; verify Redis cache hit rate
- **Payment webhook failures**: Validate signature; check idempotency key storage; verify callback URL in gateway dashboard
- **Retailer orders not appearing**: Check Kafka topic offset; verify retailer KYC status; test FCM token registration

---

## Quick References
- **OpenAPI Spec**: `./backend/openapi.yaml`
- **DB Schema**: `./wiki/Database_Schema.md` + `./wiki/Backend/Database_Schema.md`
- **Architecture Diagram**: `./wiki/Detailed Component Diagram (Services, APIs, Data Stores).md`
- **Retailer Onboarding**: `./wiki/Retailer Onboarding & KYC Flow.md`
- **Mobile Flows**: `./wiki/FLUTTER WIREFRAMES/` directory
- **Implementation Roadmap**: `./wiki/Implementation_Roadmap.md` (MVP → V1 → V2 with team estimates)
