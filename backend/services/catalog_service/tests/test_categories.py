"""Tests for category endpoints"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_category(client: AsyncClient):
    """Test creating a new category"""
    response = await client.post(
        "/api/v1/categories/",
        json={
            "name": "New Category",
            "description": "Category description",
            "display_order": 1
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "New Category"
    assert data["slug"] == "new-category"  # Auto-generated slug


@pytest.mark.asyncio
async def test_create_category_with_custom_slug(client: AsyncClient):
    """Test creating category with custom slug"""
    response = await client.post(
        "/api/v1/categories/",
        json={
            "name": "Custom Category",
            "slug": "my-custom-slug",
            "display_order": 1
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["slug"] == "my-custom-slug"


@pytest.mark.asyncio
async def test_get_category(client: AsyncClient, sample_category):
    """Test retrieving a category by ID"""
    response = await client.get(f"/api/v1/categories/{sample_category.id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(sample_category.id)
    assert data["name"] == sample_category.name


@pytest.mark.asyncio
async def test_get_category_by_slug(client: AsyncClient, sample_category):
    """Test retrieving a category by slug"""
    response = await client.get(f"/api/v1/categories/slug/{sample_category.slug}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["slug"] == sample_category.slug


@pytest.mark.asyncio
async def test_update_category(client: AsyncClient, sample_category):
    """Test updating a category"""
    response = await client.put(
        f"/api/v1/categories/{sample_category.id}",
        json={
            "name": "Updated Category",
            "display_order": 5
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Category"
    assert data["display_order"] == 5


@pytest.mark.asyncio
async def test_delete_category(client: AsyncClient, sample_category):
    """Test soft-deleting a category"""
    response = await client.delete(f"/api/v1/categories/{sample_category.id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


@pytest.mark.asyncio
async def test_list_categories(client: AsyncClient, sample_category):
    """Test listing all categories"""
    response = await client.get("/api/v1/categories/")
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


@pytest.mark.asyncio
async def test_hierarchical_categories(client: AsyncClient, db_session):
    """Test creating and listing hierarchical categories"""
    from app.models import Category
    
    # Create parent category
    parent = Category(name="Parent Category", slug="parent", display_order=1)
    db_session.add(parent)
    await db_session.commit()
    await db_session.refresh(parent)
    
    # Create child category
    child = Category(
        name="Child Category",
        slug="child",
        parent_id=parent.id,
        display_order=1
    )
    db_session.add(child)
    await db_session.commit()
    
    # List children of parent
    response = await client.get(
        "/api/v1/categories/",
        params={"parent_id": str(parent.id)}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["parent_id"] == str(parent.id)


@pytest.mark.asyncio
async def test_category_display_order(client: AsyncClient, db_session):
    """Test categories are ordered by display_order"""
    from app.models import Category
    
    # Create categories with different display orders
    for i in [3, 1, 2]:
        category = Category(
            name=f"Category {i}",
            slug=f"category-{i}",
            display_order=i
        )
        db_session.add(category)
    await db_session.commit()
    
    response = await client.get("/api/v1/categories/")
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify ordering (should be 1, 2, 3)
    display_orders = [cat["display_order"] for cat in data]
    assert display_orders == sorted(display_orders)
