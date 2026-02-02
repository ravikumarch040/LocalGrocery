# Python + FastAPI Backend Setup Guide

## Prerequisites

- **Python 3.11+** (get from https://www.python.org/)
- **pip** (comes with Python)
- **Poetry** (recommended) or **pipenv** (optional but helpful)
- **Docker & Docker Compose** (for infrastructure)
- **PostgreSQL client** (optional, for direct queries)

## Quick Start

### 1. Install Python

```powershell
# Verify Python installation
python --version  # Should be 3.11 or higher
pip --version
```

### 2. Create Virtual Environment

```powershell
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
.\venv\Scripts\Activate.ps1

# On Linux/Mac:
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip
```

### 3. Install Dependencies

```powershell
# Install core dependencies
pip install fastapi uvicorn[standard]
pip install sqlalchemy asyncpg motor pymongo
pip install pydantic python-dotenv
pip install pytest pytest-asyncio pytest-cov
pip install aioredis redis aiokafka elasticsearch
pip install requests httpx
pip install python-jose[cryptography] passlib PyJWT
pip install python-multipart

# Or use requirements.txt
pip install -r requirements.txt
```

### 4. Setup Infrastructure

```powershell
# Start all services
docker-compose -f docker-compose.dev.yml up -d

# Verify
docker ps
curl http://localhost:9200  # Elasticsearch
```

### 5. Initialize Databases

```powershell
# PostgreSQL migrations
cd ..\scripts
.\migrate-postgres.ps1 up

# MongoDB initialization
docker exec -i localgrocery-mongodb mongosh -u localgrocery -p dev_password_change_in_prod < ..\backend\database\migrations\mongodb_init.js
```

### 6. Run First Service

```powershell
cd ..\services\auth_service

# Install service dependencies
pip install -r requirements.txt

# Run development server
python -m uvicorn app.main:app --reload --port 8001

# Or using gunicorn for production-like testing
pip install gunicorn
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8001
```

---

## 📁 Service Structure Template

### Create New Service

```powershell
# Example: Creating catalog service
mkdir services\catalog_service
cd services\catalog_service

# Create app structure
mkdir app\api\v1\endpoints
mkdir app\api\v1\schemas
mkdir app\models
mkdir app\crud
mkdir app\services
mkdir app\utils
mkdir tests

# Create files
touch app\__init__.py
touch app\main.py
touch app\config.py
touch app\dependencies.py
touch app\database.py
touch requirements.txt
touch Dockerfile
touch pytest.ini
```

### Directory Structure Explanation

```
catalog_service/
├── app/
│   ├── __init__.py              # Package marker
│   ├── main.py                  # FastAPI app creation & setup
│   ├── config.py                # Configuration & settings (env vars)
│   ├── dependencies.py          # Dependency injection setup
│   ├── database.py              # Database connection setup
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── endpoints/
│   │       │   ├── __init__.py
│   │       │   ├── products.py  # Product endpoints
│   │       │   └── categories.py
│   │       │
│   │       └── schemas/         # Pydantic models (request/response)
│   │           ├── __init__.py
│   │           ├── product.py   # ProductSchema, ProductCreateSchema
│   │           └── category.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── product.py           # SQLAlchemy ORM models
│   │   └── category.py
│   │
│   ├── crud/
│   │   ├── __init__.py
│   │   ├── base.py              # CRUD base class
│   │   ├── product.py           # ProductCRUD operations
│   │   └── category.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   └── catalog.py           # Business logic
│   │
│   └── utils/
│       ├── __init__.py
│       ├── logger.py            # Logging setup
│       ├── errors.py            # Custom exceptions
│       └── validators.py        # Validation helpers
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # Pytest fixtures & setup
│   ├── test_products.py         # Product endpoint tests
│   ├── test_crud.py             # CRUD operation tests
│   └── test_services.py         # Business logic tests
│
├── requirements.txt             # Python dependencies
├── pytest.ini                   # Pytest configuration
├── Dockerfile                   # Docker image
└── README.md                    # Service documentation
```

---

## 🔧 Key Configuration Files

### requirements.txt Template

```
# requirements.txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
asyncpg==0.29.0
motor==3.3.2
pymongo==4.6.0
pydantic==2.5.0
pydantic-settings==2.1.0
python-dotenv==1.0.0
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
httpx==0.25.1
requests==2.31.0
aioredis==2.0.1
redis==5.0.1
aiokafka==0.10.0
elasticsearch==8.11.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
PyJWT==2.8.1
python-multipart==0.0.6
gunicorn==21.2.0
```

### app/config.py Template

```python
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "LocalGrocery Catalog Service"
    DEBUG: bool = False
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://localgrocery:password@localhost:5432/localgrocery"
    MONGODB_URL: str = "mongodb://localgrocery:password@localhost:27017/localgrocery"
    
    # Redis
    REDIS_URL: str = "redis://:password@localhost:6379/0"
    
    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    
    # JWT
    JWT_SECRET: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    
    # CORS
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:4200"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

### app/main.py Template

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config import settings
from app.api.v1 import endpoints

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print(f"Starting {settings.APP_NAME}...")
    yield
    # Shutdown
    print(f"Shutting down {settings.APP_NAME}...")

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(endpoints.router, prefix="/api/v1")

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
```

### app/models/product.py Template

```python
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()

class Product(Base):
    __tablename__ = "products"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(200), nullable=False, index=True)
    category = Column(String(100), nullable=False, index=True)
    brand = Column(String(100), nullable=False, index=True)
    description = Column(Text)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

### app/schemas/product.py Template

```python
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    category: str = Field(..., min_length=1, max_length=100)
    brand: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    is_active: bool = True

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    brand: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class ProductResponse(ProductBase):
    id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True  # Pydantic v2 syntax
```

### tests/conftest.py Template

```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from app.main import app
from app.database import get_db

@pytest.fixture
async def test_db():
    # Use in-memory SQLite or test PostgreSQL
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    await engine.dispose()

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
async def mock_redis(mocker):
    mock = mocker.AsyncMock()
    return mock
```

---

## 🧪 Testing Pattern

### Example: tests/test_products.py

```python
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_get_products():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/products")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_create_product():
    async with AsyncClient(app=app, base_url="http://test") as client:
        product_data = {
            "name": "Test Rice",
            "category": "Grains",
            "brand": "TestBrand"
        }
        response = await client.post("/api/v1/products", json=product_data)
        assert response.status_code == 201
        assert response.json()["name"] == "Test Rice"
```

### Running Tests

```powershell
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific file
pytest tests/test_products.py

# Run specific test
pytest tests/test_products.py::test_get_products -v
```

---

## 🚀 Running Services

### Development Mode

```powershell
cd services\auth_service

# Activate venv
.\venv\Scripts\Activate.ps1

# Run with hot-reload
python -m uvicorn app.main:app --reload --port 8001
```

### Production-like Testing

```powershell
# Using gunicorn (production ASGI server)
gunicorn app.main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8001
```

### Docker

```powershell
# Build image
docker build -t localgrocery-auth:v1.0.0 .

# Run container
docker run -p 8001:8000 \
    -e DATABASE_URL="postgresql+asyncpg://..." \
    localgrocery-auth:v1.0.0
```

---

## 📚 Useful Commands

```powershell
# Check installed packages
pip list

# Show package info
pip show fastapi

# Upgrade pip
pip install --upgrade pip

# Install from requirements
pip install -r requirements.txt

# Generate requirements
pip freeze > requirements.txt

# Clean up virtual environment
python -m pip cache purge

# Deactivate venv
deactivate
```

---

## 🐛 Troubleshooting

### PostgreSQL Connection Error
```powershell
# Check if PostgreSQL is running
docker ps | grep postgres

# Verify credentials
psql -h localhost -U localgrocery -d localgrocery
```

### Import Errors
```powershell
# Reinstall in virtual environment
pip install --force-reinstall -r requirements.txt

# Check PYTHONPATH
echo $env:PYTHONPATH
```

### Async Issues
```powershell
# Ensure pytest-asyncio is installed
pip install pytest-asyncio

# Mark async tests properly
# Add to conftest.py:
pytest_plugins = ('pytest_asyncio',)
```

---

## 📖 Learning Resources

- [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/)
- [SQLAlchemy ORM Docs](https://docs.sqlalchemy.org/orm/)
- [Pydantic Docs](https://docs.pydantic.dev/)
- [pytest Documentation](https://docs.pytest.org/)
- [Python async/await](https://docs.python.org/3/library/asyncio.html)

---

## ✅ Verification Checklist

- [ ] Python 3.11+ installed
- [ ] Virtual environment created and activated
- [ ] All dependencies installed
- [ ] PostgreSQL running (`docker ps`)
- [ ] MongoDB running (`docker ps`)
- [ ] Test database migrations work
- [ ] Can import FastAPI and SQLAlchemy
- [ ] Sample service starts without errors
- [ ] Can access Swagger UI at `/docs`

**You're ready to start building! 🚀**
