"""Test configuration and fixtures"""
import pytest
import pytest_asyncio
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database import Base, get_db
from app.models import DeliveryPartner, DeliveryPartnerStatus, VehicleType
import uuid
from datetime import datetime, UTC

# Test database URL (in-memory SQLite)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Create test session maker
TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


@pytest_asyncio.fixture(scope="function")
async def db_session():
    """Create database session for tests"""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with TestSessionLocal() as session:
        yield session
        await session.rollback()
    
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def client(db_session):
    """Create test client"""
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def sample_delivery_partner(db_session):
    """Create a sample delivery partner"""
    partner = DeliveryPartner(
        id=uuid.uuid4(),
        name="Test Partner",
        phone="9876543210",
        email="partner@test.com",
        vehicle_type=VehicleType.BIKE,
        vehicle_number="KA01AB1234",
        status=DeliveryPartnerStatus.AVAILABLE,
        is_verified=True,
        is_active=True,
        current_location={"lat": 12.9716, "lng": 77.5946},  # Bangalore
        total_deliveries=10,
        successful_deliveries=9,
        rating=4.5,
        last_active_at=datetime.now(UTC)
    )
    db_session.add(partner)
    await db_session.commit()
    await db_session.refresh(partner)
    return partner


@pytest.fixture()
def sample_delivery_data():
    """Sample delivery data"""
    return {
        "order_id": str(uuid.uuid4()),
        "pickup_location": {
            "lat": 12.9716,
            "lng": 77.5946,
            "address": "Test Store, Bangalore"
        },
        "delivery_location": {
            "lat": 12.9352,
            "lng": 77.6245,
            "address": "Test Customer, Bangalore"
        },
        "delivery_instructions": "Please call before delivery"
    }
