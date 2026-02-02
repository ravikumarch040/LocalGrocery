import pytest
import asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from datetime import datetime
import uuid

from app.main import app
from app.database import get_db, Base
from app.models import Cart, CartItem
from app.services import CartService
from app.config import settings


# ==================== Test Database Setup ====================

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = None
TestingSessionLocal = None


@pytest.fixture(scope="function")
async def test_db():
    """Create test database and session"""
    global engine, TestingSessionLocal
    
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=None
    )
    TestingSessionLocal = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield TestingSessionLocal
    
    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture
async def override_get_db():
    """Override get_db dependency"""
    async def _override_get_db():
        async with TestingSessionLocal() as session:
            yield session
    
    app.dependency_overrides[get_db] = _override_get_db
    yield
    app.dependency_overrides.clear()


@pytest.fixture
async def client(test_db, override_get_db):
    """Test client"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


# ==================== Test Data ====================

@pytest.fixture
async def sample_cart(test_db):
    """Create sample cart"""
    async with TestingSessionLocal() as session:
        cart = Cart(customer_id="customer_123")
        session.add(cart)
        await session.commit()
        await session.refresh(cart)
        return cart


@pytest.fixture
async def sample_cart_item(test_db, sample_cart):
    """Create sample cart item"""
    async with TestingSessionLocal() as session:
        item = CartItem(
            cart_id=sample_cart.id,
            product_id="prod_123",
            store_id="store_456",
            quantity=2,
            unit_price=100.0
        )
        session.add(item)
        await session.commit()
        await session.refresh(item)
        return item


# ==================== Cart Service Tests ====================

class TestCartService:
    """Tests for CartService"""
    
    @pytest.mark.asyncio
    async def test_create_cart(self, test_db):
        """Test creating a new cart"""
        async with TestingSessionLocal() as session:
            service = CartService(session)
            cart = await service.create_cart("customer_123")
            
            assert cart is not None
            assert cart.customer_id == "customer_123"
            assert len(cart.items) == 0
    
    @pytest.mark.asyncio
    async def test_get_cart(self, test_db, sample_cart):
        """Test getting cart by ID"""
        async with TestingSessionLocal() as session:
            service = CartService(session)
            cart = await service.get_cart(str(sample_cart.id))
            
            assert cart is not None
            assert str(cart.id) == str(sample_cart.id)
            assert cart.customer_id == "customer_123"
    
    @pytest.mark.asyncio
    async def test_get_active_cart(self, test_db):
        """Test getting active cart for customer"""
        async with TestingSessionLocal() as session:
            service = CartService(session)
            cart = await service.create_cart("customer_active")
            
            active_cart = await service.get_active_cart("customer_active")
            
            assert active_cart is not None
            assert str(active_cart.id) == str(cart.id)
    
    @pytest.mark.asyncio
    async def test_add_item_to_cart(self, test_db, sample_cart):
        """Test adding item to cart"""
        async with TestingSessionLocal() as session:
            service = CartService(session)
            
            item = await service.add_item(
                cart_id=str(sample_cart.id),
                product_id="prod_456",
                store_id="store_789",
                quantity=1,
                unit_price=50.0
            )
            
            assert item is not None
            assert item.product_id == "prod_456"
            assert item.quantity == 1
    
    @pytest.mark.asyncio
    async def test_add_duplicate_item_increments_quantity(self, test_db, sample_cart):
        """Test that adding duplicate item increments quantity"""
        async with TestingSessionLocal() as session:
            service = CartService(session)
            
            # Add first
            item1 = await service.add_item(
                cart_id=str(sample_cart.id),
                product_id="prod_123",
                store_id="store_456",
                quantity=1,
                unit_price=100.0
            )
            
            # Add duplicate
            item2 = await service.add_item(
                cart_id=str(sample_cart.id),
                product_id="prod_123",
                store_id="store_456",
                quantity=2,
                unit_price=100.0
            )
            
            assert str(item1.id) == str(item2.id)  # Same item
            assert item2.quantity == 3  # 1 + 2
    
    @pytest.mark.asyncio
    async def test_update_item_quantity(self, test_db, sample_cart, sample_cart_item):
        """Test updating item quantity"""
        async with TestingSessionLocal() as session:
            service = CartService(session)
            
            updated = await service.update_item_quantity(
                cart_id=str(sample_cart.id),
                item_id=str(sample_cart_item.id),
                quantity=5
            )
            
            assert updated is not None
            assert updated.quantity == 5
    
    @pytest.mark.asyncio
    async def test_remove_item(self, test_db, sample_cart, sample_cart_item):
        """Test removing item from cart"""
        async with TestingSessionLocal() as session:
            service = CartService(session)
            
            success = await service.remove_item(
                cart_id=str(sample_cart.id),
                item_id=str(sample_cart_item.id)
            )
            
            assert success is True
            
            # Verify item is gone
            item = await service.get_cart_item(str(sample_cart_item.id))
            assert item is None
    
    @pytest.mark.asyncio
    async def test_clear_cart(self, test_db, sample_cart):
        """Test clearing all items from cart"""
        async with TestingSessionLocal() as session:
            service = CartService(session)
            
            # Add items
            await service.add_item(
                cart_id=str(sample_cart.id),
                product_id="prod_1",
                store_id="store_1",
                quantity=1,
                unit_price=50.0
            )
            await service.add_item(
                cart_id=str(sample_cart.id),
                product_id="prod_2",
                store_id="store_1",
                quantity=1,
                unit_price=50.0
            )
            
            # Clear
            success = await service.clear_cart(str(sample_cart.id))
            assert success is True
            
            # Verify empty
            cart = await service.get_cart(str(sample_cart.id))
            assert len(cart.items) == 0
    
    @pytest.mark.asyncio
    async def test_calculate_cart_totals(self, test_db, sample_cart):
        """Test calculating cart totals"""
        async with TestingSessionLocal() as session:
            service = CartService(session)
            
            # Add items
            await service.add_item(
                cart_id=str(sample_cart.id),
                product_id="prod_1",
                store_id="store_1",
                quantity=2,
                unit_price=100.0  # Total: 200
            )
            await service.add_item(
                cart_id=str(sample_cart.id),
                product_id="prod_2",
                store_id="store_1",
                quantity=3,
                unit_price=50.0   # Total: 150
            )
            
            cart = await service.get_cart(str(sample_cart.id))
            totals = service.calculate_cart_totals(cart)
            
            assert totals["total_amount"] == 350.0
            assert totals["total_items"] == 5
            assert totals["items_count"] == 2
    
    @pytest.mark.asyncio
    async def test_group_items_by_store(self, test_db, sample_cart):
        """Test grouping items by store"""
        async with TestingSessionLocal() as session:
            service = CartService(session)
            
            # Add items from different stores
            await service.add_item(
                cart_id=str(sample_cart.id),
                product_id="prod_1",
                store_id="store_1",
                quantity=1,
                unit_price=100.0
            )
            await service.add_item(
                cart_id=str(sample_cart.id),
                product_id="prod_2",
                store_id="store_2",
                quantity=2,
                unit_price=50.0
            )
            
            cart = await service.get_cart(str(sample_cart.id))
            grouped = await service.group_items_by_store(cart)
            
            assert "store_1" in grouped
            assert "store_2" in grouped
            assert len(grouped["store_1"]) == 1
            assert len(grouped["store_2"]) == 1


# ==================== API Endpoint Tests ====================

class TestCartAPI:
    """Tests for Cart API endpoints"""
    
    @pytest.mark.asyncio
    async def test_create_cart_endpoint(self, client):
        """Test POST /v1/carts"""
        response = await client.post(
            "/v1/carts/",
            json={"customer_id": "customer_123"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["customer_id"] == "customer_123"
    
    @pytest.mark.asyncio
    async def test_get_cart_endpoint(self, client, test_db):
        """Test GET /v1/carts/{cart_id}"""
        # Create cart
        async with TestingSessionLocal() as session:
            service = CartService(session)
            cart = await service.create_cart("customer_123")
            cart_id = str(cart.id)
        
        # Get cart
        response = await client.get(f"/v1/carts/{cart_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["customer_id"] == "customer_123"
    
    @pytest.mark.asyncio
    async def test_add_item_endpoint(self, client, test_db):
        """Test POST /v1/carts/{cart_id}/items"""
        # Create cart
        async with TestingSessionLocal() as session:
            service = CartService(session)
            cart = await service.create_cart("customer_123")
            cart_id = str(cart.id)
        
        # Add item
        response = await client.post(
            f"/v1/carts/{cart_id}/items",
            json={
                "product_id": "prod_123",
                "store_id": "store_456",
                "quantity": 1,
                "unit_price": 100.0
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["product_id"] == "prod_123"
        assert data["quantity"] == 1
    
    @pytest.mark.asyncio
    async def test_update_item_endpoint(self, client, test_db):
        """Test PUT /v1/carts/{cart_id}/items/{item_id}"""
        # Setup
        async with TestingSessionLocal() as session:
            service = CartService(session)
            cart = await service.create_cart("customer_123")
            item = await service.add_item(
                str(cart.id), "prod_123", "store_456", 1, 100.0
            )
            cart_id = str(cart.id)
            item_id = str(item.id)
        
        # Update
        response = await client.put(
            f"/v1/carts/{cart_id}/items/{item_id}",
            json={"quantity": 5}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["quantity"] == 5
    
    @pytest.mark.asyncio
    async def test_remove_item_endpoint(self, client, test_db):
        """Test DELETE /v1/carts/{cart_id}/items/{item_id}"""
        # Setup
        async with TestingSessionLocal() as session:
            service = CartService(session)
            cart = await service.create_cart("customer_123")
            item = await service.add_item(
                str(cart.id), "prod_123", "store_456", 1, 100.0
            )
            cart_id = str(cart.id)
            item_id = str(item.id)
        
        # Remove
        response = await client.delete(f"/v1/carts/{cart_id}/items/{item_id}")
        
        assert response.status_code == 204
    
    @pytest.mark.asyncio
    async def test_health_endpoint(self, client):
        """Test /health endpoint"""
        response = await client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
