"""Tests for order endpoints"""
import pytest
from httpx import AsyncClient
from decimal import Decimal
from uuid import uuid4

from app.models import OrderStatus, PaymentStatus


@pytest.mark.asyncio
async def test_create_order(client: AsyncClient, sample_customer_id, sample_store_id, sample_product_id, sample_delivery_address):
    """Test creating a new order"""
    order_data = {
        "customer_id": str(sample_customer_id),
        "store_id": str(sample_store_id),
        "payment_method": "UPI",
        "delivery_address": sample_delivery_address,
        "items": [
            {
                "product_id": str(sample_product_id),
                "product_name": "Rice",
                "quantity": 2,
                "unit_price": "100.00"
            }
        ]
    }
    
    response = await client.post("/api/v1/orders/", json=order_data)
    assert response.status_code == 201
    data = response.json()
    assert data["order_number"].startswith("ORD-")
    assert data["status"] == "PLACED"
    assert data["payment_status"] == "PENDING"
    assert data["total_amount"] == "200.00"
    assert len(data["items"]) == 1


@pytest.mark.asyncio
async def test_create_order_invalid_address(client: AsyncClient, sample_customer_id, sample_store_id, sample_product_id):
    """Test creating order with invalid address"""
    order_data = {
        "customer_id": str(sample_customer_id),
        "store_id": str(sample_store_id),
        "payment_method": "UPI",
        "delivery_address": {"street": "123 Main"},  # Missing required fields
        "items": [
            {
                "product_id": str(sample_product_id),
                "product_name": "Rice",
                "quantity": 1,
                "unit_price": "100.00"
            }
        ]
    }
    
    response = await client.post("/api/v1/orders/", json=order_data)
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_create_order_no_items(client: AsyncClient, sample_customer_id, sample_store_id, sample_delivery_address):
    """Test creating order without items"""
    order_data = {
        "customer_id": str(sample_customer_id),
        "store_id": str(sample_store_id),
        "payment_method": "UPI",
        "delivery_address": sample_delivery_address,
        "items": []
    }
    
    response = await client.post("/api/v1/orders/", json=order_data)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_order(client: AsyncClient, sample_customer_id, sample_store_id, sample_product_id, sample_delivery_address):
    """Test retrieving an order"""
    # Create order
    order_data = {
        "customer_id": str(sample_customer_id),
        "store_id": str(sample_store_id),
        "payment_method": "UPI",
        "delivery_address": sample_delivery_address,
        "items": [
            {
                "product_id": str(sample_product_id),
                "product_name": "Rice",
                "quantity": 1,
                "unit_price": "100.00"
            }
        ]
    }
    
    create_response = await client.post("/api/v1/orders/", json=order_data)
    order_id = create_response.json()["id"]
    
    # Get order
    response = await client.get(f"/api/v1/orders/{order_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == order_id
    assert data["status"] == "PLACED"


@pytest.mark.asyncio
async def test_get_order_not_found(client: AsyncClient):
    """Test retrieving non-existent order"""
    response = await client.get(f"/api/v1/orders/{uuid4()}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_orders(client: AsyncClient, sample_customer_id, sample_store_id, sample_product_id, sample_delivery_address):
    """Test listing orders"""
    # Create multiple orders
    for i in range(3):
        order_data = {
            "customer_id": str(sample_customer_id),
            "store_id": str(sample_store_id),
            "payment_method": "UPI",
            "delivery_address": sample_delivery_address,
            "items": [
                {
                    "product_id": str(sample_product_id),
                    "product_name": f"Product {i}",
                    "quantity": i + 1,
                    "unit_price": "100.00"
                }
            ]
        }
        await client.post("/api/v1/orders/", json=order_data)
    
    # List orders
    response = await client.get(
        "/api/v1/orders/",
        params={"customer_id": str(sample_customer_id)}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3
    assert len(data["orders"]) == 3


@pytest.mark.asyncio
async def test_list_orders_pagination(client: AsyncClient, sample_customer_id, sample_store_id, sample_product_id, sample_delivery_address):
    """Test pagination in order listing"""
    # Create 5 orders
    for i in range(5):
        order_data = {
            "customer_id": str(sample_customer_id),
            "store_id": str(sample_store_id),
            "payment_method": "UPI",
            "delivery_address": sample_delivery_address,
            "items": [
                {
                    "product_id": str(sample_product_id),
                    "product_name": "Rice",
                    "quantity": 1,
                    "unit_price": "100.00"
                }
            ]
        }
        await client.post("/api/v1/orders/", json=order_data)
    
    # Get page 1
    response = await client.get(
        "/api/v1/orders/",
        params={"page": 1, "page_size": 2, "customer_id": str(sample_customer_id)}
    )
    data = response.json()
    assert len(data["orders"]) == 2
    assert data["total"] == 5
    assert data["page"] == 1


@pytest.mark.asyncio
async def test_update_order_status(client: AsyncClient, sample_customer_id, sample_store_id, sample_product_id, sample_delivery_address):
    """Test updating order status"""
    # Create order
    order_data = {
        "customer_id": str(sample_customer_id),
        "store_id": str(sample_store_id),
        "payment_method": "UPI",
        "delivery_address": sample_delivery_address,
        "items": [
            {
                "product_id": str(sample_product_id),
                "product_name": "Rice",
                "quantity": 1,
                "unit_price": "100.00"
            }
        ]
    }
    
    create_response = await client.post("/api/v1/orders/", json=order_data)
    order_id = create_response.json()["id"]
    
    # Update status to CONFIRMED
    update_data = {"status": "CONFIRMED"}
    response = await client.put(f"/api/v1/orders/{order_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "CONFIRMED"
    assert data["confirmed_at"] is not None


@pytest.mark.asyncio
async def test_update_order_invalid_status_transition(client: AsyncClient, sample_customer_id, sample_store_id, sample_product_id, sample_delivery_address):
    """Test invalid order status transition"""
    # Create order
    order_data = {
        "customer_id": str(sample_customer_id),
        "store_id": str(sample_store_id),
        "payment_method": "UPI",
        "delivery_address": sample_delivery_address,
        "items": [
            {
                "product_id": str(sample_product_id),
                "product_name": "Rice",
                "quantity": 1,
                "unit_price": "100.00"
            }
        ]
    }
    
    create_response = await client.post("/api/v1/orders/", json=order_data)
    order_id = create_response.json()["id"]
    
    # Try invalid transition from PLACED to DELIVERED
    update_data = {"status": "DELIVERED"}
    response = await client.put(f"/api/v1/orders/{order_id}", json=update_data)
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_cancel_order(client: AsyncClient, sample_customer_id, sample_store_id, sample_product_id, sample_delivery_address):
    """Test cancelling an order"""
    # Create order
    order_data = {
        "customer_id": str(sample_customer_id),
        "store_id": str(sample_store_id),
        "payment_method": "UPI",
        "delivery_address": sample_delivery_address,
        "items": [
            {
                "product_id": str(sample_product_id),
                "product_name": "Rice",
                "quantity": 1,
                "unit_price": "100.00"
            }
        ]
    }
    
    create_response = await client.post("/api/v1/orders/", json=order_data)
    order_id = create_response.json()["id"]
    
    # Cancel order
    response = await client.delete(f"/api/v1/orders/{order_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


@pytest.mark.asyncio
async def test_order_number_uniqueness(client: AsyncClient, sample_customer_id, sample_store_id, sample_product_id, sample_delivery_address):
    """Test that order numbers are unique"""
    order_data = {
        "customer_id": str(sample_customer_id),
        "store_id": str(sample_store_id),
        "payment_method": "UPI",
        "delivery_address": sample_delivery_address,
        "items": [
            {
                "product_id": str(sample_product_id),
                "product_name": "Rice",
                "quantity": 1,
                "unit_price": "100.00"
            }
        ]
    }
    
    # Create first order
    response1 = await client.post("/api/v1/orders/", json=order_data)
    order_number1 = response1.json()["order_number"]
    
    # Create second order
    response2 = await client.post("/api/v1/orders/", json=order_data)
    order_number2 = response2.json()["order_number"]
    
    assert order_number1 != order_number2


@pytest.mark.asyncio
async def test_get_order_by_number(client: AsyncClient, sample_customer_id, sample_store_id, sample_product_id, sample_delivery_address):
    """Test retrieving order by order number"""
    order_data = {
        "customer_id": str(sample_customer_id),
        "store_id": str(sample_store_id),
        "payment_method": "UPI",
        "delivery_address": sample_delivery_address,
        "items": [
            {
                "product_id": str(sample_product_id),
                "product_name": "Rice",
                "quantity": 1,
                "unit_price": "100.00"
            }
        ]
    }
    
    create_response = await client.post("/api/v1/orders/", json=order_data)
    order_number = create_response.json()["order_number"]
    
    response = await client.get(f"/api/v1/orders/number/{order_number}")
    assert response.status_code == 200
    assert response.json()["order_number"] == order_number
