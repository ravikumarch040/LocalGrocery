import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from httpx import AsyncClient, ASGITransport
from datetime import datetime, timedelta, timezone
import uuid
import json
import os

from app.main import app
from app.models import Base
from app.database import get_db


# Test Database Setup - Use PostgreSQL instead of SQLite for JSONB support
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://localgrocery:dev_password_change_in_prod@localhost:5432/localgrocery_test"
)


@pytest_asyncio.fixture
async def test_engine():
    """Create test database engine"""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def test_db(test_engine):
    """Create test database session"""
    async_session = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with async_session() as session:
        yield session


@pytest_asyncio.fixture
async def client(test_db):
    """Create test client with dependency override using ASGITransport"""
    def override_get_db():
        return test_db
    
    app.dependency_overrides[get_db] = override_get_db
    
    # Use ASGITransport to mount the app
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture
def store_id():
    return str(uuid.uuid4())


@pytest.fixture
def product_id():
    return str(uuid.uuid4())


@pytest.fixture
def customer_id():
    return str(uuid.uuid4())


@pytest.fixture
def order_id():
    return str(uuid.uuid4())


@pytest.fixture
def inventory_request(store_id, product_id):
    return {
        "store_id": store_id,
        "product_id": product_id,
        "stock_qty": 100,
        "cost_price": 50.0,
        "selling_price": 100.0,
        "reorder_level": 10,
        "reorder_qty": 50,
        "supplier_id": str(uuid.uuid4()),
        "batch_number": "BATCH123",
        "product_metadata": {"sku": "SKU123", "barcode": "1234567890"},
    }
