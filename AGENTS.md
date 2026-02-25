# AGENTS.md

## Cursor Cloud specific instructions

### Overview

LocalGrocery is a hyperlocal multi-vendor grocery marketplace. The backend is Python 3.12 / FastAPI microservices under `backend/services/`. Infrastructure (PostgreSQL 15, Redis 7, PgBouncer) runs via Docker Compose at `backend/docker-compose.dev.yml`.

### Starting infrastructure

```bash
sudo dockerd &>/dev/null &   # only if Docker daemon is not already running
sudo docker compose -f backend/docker-compose.dev.yml up -d
```

Ports: PostgreSQL 5432, Redis 6379, PgBouncer 6432. Credentials: user `localgrocery`, password `dev_password_change_in_prod`.

### Database setup

A `localgrocery_test` database is needed for tests:
```bash
PGPASSWORD='dev_password_change_in_prod' psql -h localhost -U localgrocery -d localgrocery -c "CREATE DATABASE localgrocery_test;"
PGPASSWORD='dev_password_change_in_prod' psql -h localhost -U localgrocery -d localgrocery_test -c "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\"; CREATE EXTENSION IF NOT EXISTS \"pg_trgm\";"
```

Schema migration: `PGPASSWORD='dev_password_change_in_prod' psql -h localhost -U localgrocery -d localgrocery -f backend/database/migrations/001_initial_schema.sql`

### Python virtual environment

The venv lives at `backend/venv`. Activate with `source backend/venv/bin/activate`.

### Running services

Each service runs via uvicorn from its own directory (the `.env` file is loaded relative to cwd):
```bash
cd backend/services/auth_service && python -m uvicorn app.main:app --reload --port 8001
cd backend/services/inventory_service && python -m uvicorn app.main:app --reload --port 8004
```
Swagger UI at `http://localhost:<port>/docs`.

### Running tests

```bash
cd backend/services/<service_name> && python -m pytest tests/ -v
```

Services with passing tests: `inventory_service` (18 tests), `order_service` (12 tests).

### Linting

```bash
source backend/venv/bin/activate
black --check backend/services/
isort --check-only backend/services/
flake8 backend/services/ --max-line-length 120
```

### Known issues (pre-existing)

- `backend/requirements.txt` pins `PyJWT==2.8.1` which does not exist on PyPI. Install with `PyJWT>=2.8.0,<3.0.0` instead.
- Different services pin different versions of shared deps (fastapi, pydantic, sqlalchemy). Installing all per-service requirements into one venv can cause version conflicts. The last-installed version wins.
- `catalog_service` startup fails with `icon_url` column mismatch — the SQLAlchemy model references `icon_url` but the migration creates `image_url`.
- `catalog_service` `.env.example` uses comma-separated `CORS_ORIGINS` which newer pydantic-settings rejects; use JSON array format `["http://localhost:3000"]`.
- Auth service `.env` must not include `NODE_ENV` or other fields not in its Settings model (pydantic forbids extra inputs).
- `delivery_service` tests fail with SQLAlchemy compile errors (pre-existing model issues).
