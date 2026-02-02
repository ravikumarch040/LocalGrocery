"""Test configuration and fixtures"""
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from httpx import AsyncClient, ASGITransport
import os

from app.main import create_app
from app.database import Base, get_db
from app.config import settings

# Test database URL (use separate test database)
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://localgrocery:dev_password_change_in_prod@localhost:5432/localgrocery_test"
)


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    """Create test database engine"""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        poolclass=NullPool,
        pool_pre_ping=True
    )
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Drop all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(test_engine):
    """Create test database session with cleanup"""
    async_session = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False
    )
    
    async with async_session() as session:
        # Clean up before test
        await session.execute(text("DELETE FROM store_products"))
        await session.execute(text("DELETE FROM products"))
        await session.execute(text("DELETE FROM categories"))
        await session.commit()
        
        yield session
        
        # Clean up after test
        await session.rollback()
        await session.execute(text("DELETE FROM store_products"))
        await session.execute(text("DELETE FROM products"))
        await session.execute(text("DELETE FROM categories"))
        await session.commit()


@pytest_asyncio.fixture
async def client(db_session):
    """Create test client with dependency override"""
    app = create_app()
    
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def sample_category(db_session):
    """Create a sample category for testing"""
    from app.models import Category
    
    category = Category(
        name="Test Category",
        slug="test-category",
        description="Test category description",
        display_order=1
    )
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)
    return category


@pytest_asyncio.fixture
async def sample_product(db_session, sample_category):
    """Create a sample product for testing"""
    from app.models import Product
    from decimal import Decimal
    
    product = Product(
        name="Test Product",
        description="Test product description",
        category_id=sample_category.id,
        base_price=Decimal("99.99"),
        unit="piece",
        variants=[
            {"name": "Small", "price": 79.99, "sku": "TST-S"},
            {"name": "Large", "price": 119.99, "sku": "TST-L"}
        ]
    )
    db_session.add(product)
    await db_session.commit()
    await db_session.refresh(product)
    return product
