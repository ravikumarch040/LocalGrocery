# LocalGrocery - Hyperlocal Grocery Marketplace Platform

A multi-vendor grocery marketplace empowering local retailers (kirana stores) in India through mobile-first architecture with three Flutter apps connecting to microservices backend.

## 🎯 Project Overview

**Mission**: Enable local retailers to sell online competitively while delivering fast, trusted grocery experiences to customers in Tier-2/3 Indian cities.

### Key Features
- **Multi-vendor marketplace** with flexible delivery models
- **Three mobile apps**: Customer, Retailer, Delivery Partner
- **Event-driven microservices** architecture
- **Dual-database pattern**: PostgreSQL (transactions) + MongoDB (catalog)
- **Real-time inventory** management with Redis caching
- **Dual payment gateways**: Razorpay + Cashfree fallback
- **Advanced search** with Elasticsearch geo-proximity
- **KYC compliance** for retailer onboarding

---

## 🏗️ Architecture

```
Flutter Apps (3) → API Gateway → Microservices → Data Layer
                                      ↓
                                   Kafka Events
```

### Core Components
1. **Mobile Apps** (Flutter/Dart + Riverpod)
   - Customer App
   - Retailer App  
   - Delivery Partner App

2. **Backend Services** (Node.js/TypeScript - NestJS)
   - Auth Service (JWT + OTP)
   - Catalog Service
   - Inventory Service
   - Cart Service
   - Order Service
   - Payment Service
   - Notification Service (FCM + MSG91)

3. **Data Stores**
   - PostgreSQL: Orders, payments, settlements, users
   - MongoDB: Product catalog with variants
   - Redis: Cart, inventory cache, sessions
   - Elasticsearch: Geo-aware product search
   - Kafka: Event streaming

4. **Infrastructure**
   - API Gateway (Kong/AWS API Gateway)
   - Docker + Kubernetes (EKS)
   - Prometheus + Grafana (monitoring)
   - ELK/OpenSearch (logging)

---

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ (Legacy) / **Python 3.11+** (Current)
- Docker & Docker Compose
- Flutter 3.16+
- PowerShell 7+ (Windows) or Bash (Linux/Mac)
- PostgreSQL client (`psql`)

### 1. Clone & Setup

```powershell
git clone <repository-url>
cd LocalGrocery

# Start MVP infrastructure (PostgreSQL, Redis, PgBouncer)
cd backend
docker-compose -f docker-compose.dev.yml up -d

# Verify services
docker ps
redis-cli ping  # Redis health check
psql -h localhost -U localgrocery -c "SELECT version()"  # PostgreSQL
```

### 2. Initialize Database

```powershell
# Copy environment template
cd backend
cp .env.example .env.local

# Edit .env.local with your API keys

# Run PostgreSQL migrations (includes FTS + Outbox table)
cd ..\scripts
.\migrate-postgres.ps1 up

# Verify setup
$env:PGPASSWORD='dev_password_change_in_prod'
psql -h localhost -U localgrocery -d localgrocery -c "\d outbox_events"
```

### 3. Run Backend Services

```powershell
# Setup Python environment
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Navigate to service and start
cd services\auth_service
python -m uvicorn app.main:app --reload --port 8001

# Access Swagger UI: http://localhost:8001/docs
```

### 4. Run Flutter Apps

```powershell
cd mobile\customer-app
flutter pub get
flutter run
```

---

## 📂 Project Structure

```
LocalGrocery/
├── backend/
│   ├── services/                 # Microservices (Python + FastAPI)
│   │   ├── auth_service/
│   │   ├── catalog_service/
│   │   ├── inventory_service/
│   │   ├── cart_service/
│   │   ├── order_service/
│   │   ├── payment_service/
│   │   └── notification_service/
│   ├── database/
│   │   └── migrations/           # PostgreSQL migration scripts
│   ├── docker-compose.dev.yml    # MVP infrastructure (PostgreSQL, Redis, PgBouncer)
│   ├── openapi.yaml              # API specifications
│   ├── requirements.txt          # Python dependencies
│   └── README.md
├── mobile/
│   ├── customer-app/             # Customer Flutter app
│   ├── retailer-app/             # Retailer Flutter app
│   └── delivery-app/             # Delivery partner app
├── scripts/
│   ├── migrate-postgres.ps1      # DB migration (Windows)
│   └── migrate-postgres.sh       # DB migration (Linux/Mac)
├── wiki/                         # Documentation
├── .github/
│   ├── copilot-instructions.md   # AI agent guidelines
│   └── IMPLEMENTATION_CHECKLIST.md
└── README.md
```

---

## 🛠️ Development Workflow

### Local Development Stack (MVP)

| Service | Port | Credentials |
|---------|------|-------------|
| PostgreSQL | 5432 | `localgrocery` / `dev_password_change_in_prod` |
| Redis | 6379 | Password: `dev_password_change_in_prod` |
| PgBouncer | 6432 | Connection pooler |

### Running Tests

```powershell
# Backend unit tests (Python)
cd backend\services\auth_service
pytest

# With coverage
pytest --cov=app

# Integration tests
pytest tests/integration/

# E2E tests
pytest tests/e2e/

# Flutter tests
cd mobile\customer-app
flutter test
```

### API Testing

```powershell
# Import OpenAPI spec into Postman
# File: backend/openapi.yaml

# Or use curl
curl http://localhost:3000/v1/auth/otp/send -X POST -H "Content-Type: application/json" -d "{\"phone\":\"9876543210\"}"
```

---

## 📊 Implementation Progress

Track implementation progress in [IMPLEMENTATION_CHECKLIST.md](.github/IMPLEMENTATION_CHECKLIST.md)

**Current Status**: 
- ✅ MVP Phase: Stack Migration (PostgreSQL + Redis + Outbox pattern)
- ✅ MVP Phase: Infrastructure Setup (Docker, Python environment)
- ⏳ MVP Phase: Core Services Implementation (Auth → Catalog → Cart → Order → Payment)
- 📋 V1 Phase: Marketplace Features (Planned)
- 📋 V2 Phase: AI/ML & Advanced Features (Planned)

### MVP Milestone (14-18 weeks with MVP stack)
- [x] Stack migration to MVP architecture
- [x] Docker infrastructure setup (PostgreSQL, Redis)
- [x] Python + FastAPI environment
- [x] PostgreSQL schema with FTS + Outbox
- [ ] Auth Service (JWT + OTP)
- [ ] Core microservices (6 services)
- [ ] API Gateway
- [ ] Flutter apps (3 apps)
- [ ] Basic admin panel

---

## 🔐 Security Checklist

- [ ] JWT tokens: 15-min access, 7-day refresh
- [ ] OTP: 6-digit, 10-min validity, rate-limited
- [ ] Payment: Gateway tokenization (no card storage)
- [ ] Database: SSL connections, encryption at rest
- [ ] Secrets: AWS Secrets Manager (no hardcoded keys)
- [ ] WAF: SQL injection, XSS protection
- [ ] RBAC: Role-based access (CUSTOMER/RETAILER/DRIVER/ADMIN)

---

## 📖 Documentation

- [Product marketing site (GitHub Pages)](website/) — static landing in `website/`; enable **Settings → Pages → GitHub Actions**, then open `https://<your-github-user-or-org>.github.io/<repository-name>/` after the deploy workflow succeeds.
- [Architecture Overview](wiki/Design_and_Architecture.md)
- [Database Schema](wiki/Database_Schema.md)
- [API Contracts](backend/openapi.yaml)
- [Retailer KYC Flow](wiki/Retailer%20Onboarding%20%26%20KYC%20Flow.md)
- [Implementation Roadmap](wiki/Implementation%20Roadmap.md)
- [Copilot Instructions](.github/copilot-instructions.md)
- [Backend Setup Guide](backend/README.md)

---

## 🤝 Contributing

1. Check [IMPLEMENTATION_CHECKLIST.md](.github/IMPLEMENTATION_CHECKLIST.md) for pending tasks
2. Create feature branch from `main`
3. Follow coding conventions in [copilot-instructions.md](.github/copilot-instructions.md)
4. Write tests for new features
5. Update OpenAPI spec for API changes
6. Submit PR with task checklist reference

---

## 📞 Support & Contact

- **Documentation**: See [wiki/](wiki/) directory
- **Issues**: Track in GitHub Issues
- **Architecture Questions**: See [Design_and_Architecture.md](wiki/Design_and_Architecture.md)

---

## 📜 License

Copyright © 2026 LocalGrocery Platform

---

## 🎯 Next Steps

### For Developers
1. ✅ **Setup Complete**: Infrastructure is ready
2. ⏳ **Next**: Implement Auth Service
3. ⏳ **Then**: Build remaining core services
4. ⏳ **After**: Create API Gateway & Flutter apps

### Quick Commands

```powershell
# Start MVP infrastructure (PostgreSQL, Redis, PgBouncer)
cd backend
docker-compose -f docker-compose.dev.yml up -d

# Check services
docker ps
redis-cli ping
psql -h localhost -U localgrocery -c "SELECT version()"

# Initialize database
cd ..\scripts
.\migrate-postgres.ps1 up

# Setup Python environment
cd ..\backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Start development
cd services\auth_service
python -m uvicorn app.main:app --reload --port 8001
```
.\migrate-postgres.ps1 up

# Setup Python environment
cd ..\backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Start development
cd services\auth_service
python -m uvicorn app.main:app --reload --port 8001
```

---

**Built with ❤️ for empowering local retailers in India**
