import pytest
from httpx import AsyncClient
import uuid
import json
from datetime import datetime, timedelta, timezone


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """Test health check endpoint"""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "inventory_service"


@pytest.mark.asyncio
async def test_create_inventory(client: AsyncClient, inventory_request):
    """Test inventory creation"""
    response = await client.post("/v1/inventory", json=inventory_request)
    assert response.status_code == 201
    data = response.json()
    assert data["store_id"] == inventory_request["store_id"]
    assert data["product_id"] == inventory_request["product_id"]
    assert data["stock_qty"] == 100
    assert data["selling_price"] == 100.0
    assert data["status"] == "IN_STOCK"


@pytest.mark.asyncio
async def test_create_inventory_out_of_stock(client: AsyncClient, store_id, product_id):
    """Test inventory creation with zero stock"""
    request = {
        "store_id": store_id,
        "product_id": product_id,
        "stock_qty": 0,
        "cost_price": 50.0,
        "selling_price": 100.0,
    }
    response = await client.post("/v1/inventory", json=request)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "OUT_OF_STOCK"


@pytest.mark.asyncio
async def test_create_duplicate_inventory(client: AsyncClient, inventory_request):
    """Test preventing duplicate inventory"""
    # Create first
    response1 = await client.post("/v1/inventory", json=inventory_request)
    assert response1.status_code == 201
    
    # Try duplicate
    response2 = await client.post("/v1/inventory", json=inventory_request)
    assert response2.status_code == 409


@pytest.mark.asyncio
async def test_get_inventory(client: AsyncClient, inventory_request):
    """Test fetching inventory"""
    # Create
    create_resp = await client.post("/v1/inventory", json=inventory_request)
    assert create_resp.status_code == 201
    
    # Get
    store_id = inventory_request["store_id"]
    product_id = inventory_request["product_id"]
    get_resp = await client.get(f"/v1/inventory/{store_id}/{product_id}")
    assert get_resp.status_code == 200
    data = get_resp.json()
    assert data["stock_qty"] == 100
    assert data["available_qty"] == 100


@pytest.mark.asyncio
async def test_get_inventory_not_found(client: AsyncClient, store_id, product_id):
    """Test getting non-existent inventory"""
    response = await client.get(f"/v1/inventory/{store_id}/{product_id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_check_availability_all_available(client: AsyncClient, inventory_request):
    """Test availability check when items are in stock"""
    # Create inventory
    await client.post("/v1/inventory", json=inventory_request)
    
    # Check availability
    check_req = {
        "items": [
            {
                "store_id": inventory_request["store_id"],
                "product_id": inventory_request["product_id"],
                "qty": 50,
            }
        ]
    }
    response = await client.post("/v1/inventory/check-availability", json=check_req)
    assert response.status_code == 200
    data = response.json()
    assert data["all_available"] is True
    assert len(data["items"]) == 1


@pytest.mark.asyncio
async def test_check_availability_insufficient_stock(client: AsyncClient, inventory_request):
    """Test availability check when stock insufficient"""
    # Create inventory with low stock
    inventory_request["stock_qty"] = 10
    await client.post("/v1/inventory", json=inventory_request)
    
    # Check availability for more than stock
    check_req = {
        "items": [
            {
                "store_id": inventory_request["store_id"],
                "product_id": inventory_request["product_id"],
                "qty": 50,
            }
        ]
    }
    response = await client.post("/v1/inventory/check-availability", json=check_req)
    assert response.status_code == 200
    data = response.json()
    assert data["all_available"] is False
    assert len(data["items"]) == 1
    assert data["items"][0]["in_stock"] is False


@pytest.mark.asyncio
async def test_adjust_stock_add(client: AsyncClient, inventory_request):
    """Test adding stock"""
    # Create
    await client.post("/v1/inventory", json=inventory_request)
    
    # Add stock
    store_id = inventory_request["store_id"]
    product_id = inventory_request["product_id"]
    adjust_req = {
        "qty_change": 50,
        "source": "MANUAL_ADJUSTMENT",
        "user_id": str(uuid.uuid4()),
        "notes": "Stock received from supplier",
    }
    response = await client.post(
        f"/v1/inventory/{store_id}/{product_id}/adjust",
        json=adjust_req,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["stock_qty"] == 150
    assert data["available_qty"] == 150


@pytest.mark.asyncio
async def test_adjust_stock_remove(client: AsyncClient, inventory_request):
    """Test removing stock"""
    await client.post("/v1/inventory", json=inventory_request)
    
    store_id = inventory_request["store_id"]
    product_id = inventory_request["product_id"]
    adjust_req = {
        "qty_change": -30,
        "source": "DAMAGE",
        "notes": "Damaged items",
    }
    response = await client.post(
        f"/v1/inventory/{store_id}/{product_id}/adjust",
        json=adjust_req,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["stock_qty"] == 70


@pytest.mark.asyncio
async def test_adjust_stock_negative_overflow(client: AsyncClient, inventory_request):
    """Test preventing negative stock"""
    await client.post("/v1/inventory", json=inventory_request)
    
    store_id = inventory_request["store_id"]
    product_id = inventory_request["product_id"]
    adjust_req = {
        "qty_change": -200,
        "source": "TEST",
    }
    response = await client.post(
        f"/v1/inventory/{store_id}/{product_id}/adjust",
        json=adjust_req,
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_reserve_inventory_success(client: AsyncClient, inventory_request, customer_id, order_id):
    """Test successful inventory reservation"""
    # Create inventory
    await client.post("/v1/inventory", json=inventory_request)
    
    # Reserve
    reserve_req = {
        "order_id": order_id,
        "customer_id": customer_id,
        "items": [
            {
                "store_id": inventory_request["store_id"],
                "product_id": inventory_request["product_id"],
                "qty": 30,
            }
        ],
    }
    response = await client.post("/v1/reservations", json=reserve_req)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "RESERVED"
    assert len(data["items"]) == 1


@pytest.mark.asyncio
async def test_reserve_inventory_insufficient_stock(client: AsyncClient, inventory_request, customer_id, order_id):
    """Test reservation with insufficient stock"""
    # Create with low stock
    inventory_request["stock_qty"] = 10
    await client.post("/v1/inventory", json=inventory_request)
    
    # Try to reserve more
    reserve_req = {
        "order_id": order_id,
        "customer_id": customer_id,
        "items": [
            {
                "store_id": inventory_request["store_id"],
                "product_id": inventory_request["product_id"],
                "qty": 50,
            }
        ],
    }
    response = await client.post("/v1/reservations", json=reserve_req)
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_confirm_reservation(client: AsyncClient, inventory_request, customer_id, order_id):
    """Test confirming reservation after payment"""
    # Create & reserve
    await client.post("/v1/inventory", json=inventory_request)
    reserve_req = {
        "order_id": order_id,
        "customer_id": customer_id,
        "items": [
            {
                "store_id": inventory_request["store_id"],
                "product_id": inventory_request["product_id"],
                "qty": 30,
            }
        ],
    }
    await client.post("/v1/reservations", json=reserve_req)
    
    # Confirm
    confirm_req = {"reason": "Payment successful"}
    response = await client.post(f"/v1/reservations/{order_id}/confirm", json=confirm_req)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "CONFIRMED"


@pytest.mark.asyncio
async def test_cancel_reservation(client: AsyncClient, inventory_request, customer_id, order_id):
    """Test cancelling reservation and restoring stock"""
    # Create inventory
    await client.post("/v1/inventory", json=inventory_request)
    
    # Get initial state
    store_id = inventory_request["store_id"]
    product_id = inventory_request["product_id"]
    initial = await client.get(f"/v1/inventory/{store_id}/{product_id}")
    initial_available = initial.json()["available_qty"]
    
    # Reserve
    reserve_req = {
        "order_id": order_id,
        "customer_id": customer_id,
        "items": [
            {
                "store_id": store_id,
                "product_id": product_id,
                "qty": 30,
            }
        ],
    }
    await client.post("/v1/reservations", json=reserve_req)
    
    # Check reserved state
    after_reserve = await client.get(f"/v1/inventory/{store_id}/{product_id}")
    assert after_reserve.json()["available_qty"] == initial_available - 30
    
    # Cancel
    cancel_req = {"reason": "User cancelled order"}
    response = await client.post(f"/v1/reservations/{order_id}/cancel", json=cancel_req)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "CANCELLED"
    
    # Check stock restored
    after_cancel = await client.get(f"/v1/inventory/{store_id}/{product_id}")
    assert after_cancel.json()["available_qty"] == initial_available


@pytest.mark.asyncio
async def test_multiple_items_reservation(client: AsyncClient, store_id, customer_id, order_id):
    """Test reserving multiple items from same order"""
    # Create two inventories
    product1_id = str(uuid.uuid4())
    product2_id = str(uuid.uuid4())
    
    inv1_req = {
        "store_id": store_id,
        "product_id": product1_id,
        "stock_qty": 100,
        "cost_price": 50.0,
        "selling_price": 100.0,
    }
    inv2_req = {
        "store_id": store_id,
        "product_id": product2_id,
        "stock_qty": 50,
        "cost_price": 30.0,
        "selling_price": 60.0,
    }
    
    await client.post("/v1/inventory", json=inv1_req)
    await client.post("/v1/inventory", json=inv2_req)
    
    # Reserve both
    reserve_req = {
        "order_id": order_id,
        "customer_id": customer_id,
        "items": [
            {"store_id": store_id, "product_id": product1_id, "qty": 20},
            {"store_id": store_id, "product_id": product2_id, "qty": 10},
        ],
    }
    response = await client.post("/v1/reservations", json=reserve_req)
    assert response.status_code == 201
    data = response.json()
    assert len(data["items"]) == 2


@pytest.mark.asyncio
async def test_partial_reservation_failure(client: AsyncClient, store_id, customer_id, order_id):
    """Test reservation failure when one item is out of stock"""
    # Create two inventories, one with low stock
    product1_id = str(uuid.uuid4())
    product2_id = str(uuid.uuid4())
    
    inv1_req = {
        "store_id": store_id,
        "product_id": product1_id,
        "stock_qty": 100,
        "cost_price": 50.0,
        "selling_price": 100.0,
    }
    inv2_req = {
        "store_id": store_id,
        "product_id": product2_id,
        "stock_qty": 5,  # Low stock
        "cost_price": 30.0,
        "selling_price": 60.0,
    }
    
    await client.post("/v1/inventory", json=inv1_req)
    await client.post("/v1/inventory", json=inv2_req)
    
    # Try to reserve both (second should fail)
    reserve_req = {
        "order_id": order_id,
        "customer_id": customer_id,
        "items": [
            {"store_id": store_id, "product_id": product1_id, "qty": 20},
            {"store_id": store_id, "product_id": product2_id, "qty": 10},  # More than available
        ],
    }
    response = await client.post("/v1/reservations", json=reserve_req)
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_get_audit_logs(client: AsyncClient, inventory_request):
    """Test fetching audit logs"""
    # Create inventory (generates log)
    create_resp = await client.post("/v1/inventory", json=inventory_request)
    inventory_id = create_resp.json()["id"]
    
    # Adjust stock (generates log)
    store_id = inventory_request["store_id"]
    product_id = inventory_request["product_id"]
    adjust_req = {
        "qty_change": 20,
        "source": "MANUAL_ADJUSTMENT",
    }
    await client.post(f"/v1/inventory/{store_id}/{product_id}/adjust", json=adjust_req)
    
    # Get audit logs
    response = await client.get(f"/v1/audit-logs/{inventory_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["count"] >= 2  # At least creation and adjustment logs
