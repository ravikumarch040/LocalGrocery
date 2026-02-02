# Backend Setup & Running Guide

## Prerequisites
- Python 3.11+
- PostgreSQL running
- Redis running

## Starting Backend Services for Development

### Option 1: Using Docker Compose (Recommended)
```powershell
cd backend
docker-compose -f docker-compose.dev.yml up -d
```

This will start:
- PostgreSQL (port 5432)
- Redis (port 6379)
- MongoDB (port 27017)
- Kafka (port 9092)
- Elasticsearch (port 9200)

### Option 2: Manual Setup
```powershell
# Setup Python environment
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Run Auth Service
cd services\auth_service
python -m uvicorn app.main:app --reload --port 8001

# (In new terminal) Run Catalog Service
cd services\catalog_service
python -m uvicorn app.main:app --reload --port 8002

# (In new terminal) Run Cart Service
cd services\cart_service
python -m uvicorn app.main:app --reload --port 8003

# (In new terminal) Run Order Service
cd services\order_service
python -m uvicorn app.main:app --reload --port 8004
```

## Testing Auth Service

Once the auth service is running on port 8001:

### Send OTP
```bash
curl -X POST http://localhost:8001/v1/auth/otp/send \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "9876543210"}'
```

### Verify OTP (default test OTP: 123456)
```bash
curl -X POST http://localhost:8001/v1/auth/otp/verify \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "9876543210", "otp": "123456"}'
```

## Environment Setup
- Copy `.env.dev` from root to `apps/customer_app/`
- Update URLs if services are running on different ports
- Default URLs point to localhost:8001-8008

## Troubleshooting

### "Failed to send OTP" Error
1. Verify backend services are running: `curl http://localhost:8001/docs`
2. Check terminal for error messages
3. Verify network connectivity
4. Check auth service logs

### Connection Refused
- Services not running on expected ports
- Firewall blocking localhost connections
- Wrong port configured in `.env.dev`

### Database Connection Error
- PostgreSQL not running
- Database credentials in `.env` incorrect
- Run migrations: `cd scripts` then `.\migrate-postgres.ps1 up`
