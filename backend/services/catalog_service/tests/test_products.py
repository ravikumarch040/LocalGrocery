"""Tests for product endpoints"""
import pytest
from httpx import AsyncClient
from decimal import Decimal


@pytest.mark.asyncio
async def test_create_product(client: AsyncClient, sample_category):
    """Test creating a new product"""
    response = await client.post(
        "/api/v1/products/",
        json={
            "name": "New Product",
            "description": "Product description",
            "category_id": str(sample_category.id),
            "base_price": 49.99,
            "unit": "kg",
            "variants": [
                {"name": "1kg", "price": 49.99, "sku": "NEW-1KG"}
            ]
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "New Product"
    assert data["base_price"] == "49.99"
    assert len(data["variants"]) == 1


@pytest.mark.asyncio
async def test_get_product(client: AsyncClient, sample_product):
    """Test retrieving a product by ID"""
    response = await client.get(f"/api/v1/products/{sample_product.id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(sample_product.id)
    assert data["name"] == sample_product.name


@pytest.mark.asyncio
async def test_get_product_not_found(client: AsyncClient):
    """Test retrieving non-existent product"""
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = await client.get(f"/api/v1/products/{fake_id}")
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_product(client: AsyncClient, sample_product):
    """Test updating a product"""
    response = await client.put(
        f"/api/v1/products/{sample_product.id}",
        json={
            "name": "Updated Product Name",
            "base_price": 129.99
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Product Name"
    assert data["base_price"] == "129.99"


@pytest.mark.asyncio
async def test_delete_product(client: AsyncClient, sample_product):
    """Test soft-deleting a product"""
    response = await client.delete(f"/api/v1/products/{sample_product.id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    
    # Verify product is soft-deleted (is_active = False)
    get_response = await client.get(f"/api/v1/products/{sample_product.id}")
    # Should still exist but marked inactive
    assert get_response.status_code == 200
    assert get_response.json()["is_active"] is False


@pytest.mark.asyncio
async def test_list_products(client: AsyncClient, sample_product, sample_category):
    """Test listing products with filters"""
    response = await client.get(
        "/api/v1/products/",
        params={"category_id": str(sample_category.id)}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert len(data["products"]) >= 1
    assert data["products"][0]["category_id"] == str(sample_category.id)


@pytest.mark.asyncio
async def test_list_products_with_price_filter(client: AsyncClient, sample_product):
    """Test listing products with price range filter"""
    response = await client.get(
        "/api/v1/products/",
        params={"min_price": 50, "max_price": 150}
    )
    
    assert response.status_code == 200
    data = response.json()
    for product in data["products"]:
        price = Decimal(product["base_price"])
        assert 50 <= price <= 150


@pytest.mark.asyncio
async def test_search_products(client: AsyncClient, sample_product):
    """Test full-text search for products"""
    response = await client.get(
        "/api/v1/products/search/",
        params={"q": "Test Product"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    # Verify search result contains our test product
    product_names = [p["name"] for p in data["products"]]
    assert "Test Product" in product_names


@pytest.mark.asyncio
async def test_search_products_min_length(client: AsyncClient):
    """Test search requires minimum query length"""
    response = await client.get(
        "/api/v1/products/search/",
        params={"q": "a"}  # Too short
    )
    
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_pagination(client: AsyncClient, db_session, sample_category):
    """Test product listing pagination"""
    from app.models import Product
    
    # Create multiple products
    for i in range(5):
        product = Product(
            name=f"Product {i}",
            category_id=sample_category.id,
            base_price=Decimal("10.00"),
            unit="piece"
        )
        db_session.add(product)
    await db_session.commit()
    
    # Test pagination
    response = await client.get(
        "/api/v1/products/",
        params={"page": 1, "page_size": 2}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["products"]) == 2
    assert data["page"] == 1
    assert data["page_size"] == 2
