"""Tests for Delivery Service"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Delivery, DeliveryStatus, DeliveryPartner
from app.services.delivery_service import DeliveryService
import uuid


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """Test health check endpoint"""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "delivery_service"


@pytest.mark.asyncio
async def test_create_delivery(client: AsyncClient, sample_delivery_data):
    """Test delivery creation"""
    response = await client.post("/v1/deliveries", json=sample_delivery_data)
    assert response.status_code == 201
    data = response.json()
    
    assert data["order_id"] == sample_delivery_data["order_id"]
    assert data["status"] == "PENDING"
    assert data["distance_km"] is not None
    assert data["estimated_time_minutes"] is not None
    assert data["delivery_fee"] is not None
    assert float(data["delivery_fee"]) >= 20.0  # Base fee


@pytest.mark.asyncio
async def test_assign_delivery_auto(
    client: AsyncClient,
    db_session: AsyncSession,
    sample_delivery_partner,
    sample_delivery_data
):
    """Test automatic delivery assignment"""
    # Create delivery
    response = await client.post("/v1/deliveries", json=sample_delivery_data)
    assert response.status_code == 201
    delivery_id = response.json()["id"]
    
    # Assign delivery (auto)
    response = await client.post(
        f"/v1/deliveries/{delivery_id}/assign",
        json={}
    )
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "ASSIGNED"
    assert data["delivery_partner_id"] == str(sample_delivery_partner.id)
    assert data["partner_name"] == sample_delivery_partner.name
    assert data["assigned_at"] is not None


@pytest.mark.asyncio
async def test_assign_delivery_manual(
    client: AsyncClient,
    db_session: AsyncSession,
    sample_delivery_partner,
    sample_delivery_data
):
    """Test manual delivery assignment"""
    # Create delivery
    response = await client.post("/v1/deliveries", json=sample_delivery_data)
    assert response.status_code == 201
    delivery_id = response.json()["id"]
    
    # Assign delivery (manual)
    response = await client.post(
        f"/v1/deliveries/{delivery_id}/assign",
        json={"delivery_partner_id": str(sample_delivery_partner.id)}
    )
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "ASSIGNED"
    assert data["delivery_partner_id"] == str(sample_delivery_partner.id)


@pytest.mark.asyncio
async def test_update_delivery_status(
    client: AsyncClient,
    db_session: AsyncSession,
    sample_delivery_partner,
    sample_delivery_data
):
    """Test delivery status updates"""
    # Create and assign delivery
    response = await client.post("/v1/deliveries", json=sample_delivery_data)
    delivery_id = response.json()["id"]
    
    await client.post(
        f"/v1/deliveries/{delivery_id}/assign",
        json={"delivery_partner_id": str(sample_delivery_partner.id)}
    )
    
    # Update to PICKED_UP
    response = await client.patch(
        f"/v1/deliveries/{delivery_id}/status",
        json={
            "status": "PICKED_UP",
            "location": {"lat": 12.9716, "lng": 77.5946}
        }
    )
    assert response.status_code == 200
    assert response.json()["status"] == "PICKED_UP"
    assert response.json()["picked_up_at"] is not None
    
    # Update to IN_TRANSIT
    response = await client.patch(
        f"/v1/deliveries/{delivery_id}/status",
        json={"status": "IN_TRANSIT"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "IN_TRANSIT"
    
    # Update to DELIVERED
    response = await client.patch(
        f"/v1/deliveries/{delivery_id}/status",
        json={"status": "DELIVERED"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "DELIVERED"
    assert data["delivered_at"] is not None
    assert data["actual_time_minutes"] is not None


@pytest.mark.asyncio
async def test_invalid_status_transition(
    client: AsyncClient,
    sample_delivery_data
):
    """Test invalid status transition"""
    # Create delivery
    response = await client.post("/v1/deliveries", json=sample_delivery_data)
    delivery_id = response.json()["id"]
    
    # Try to update to DELIVERED directly (invalid)
    response = await client.patch(
        f"/v1/deliveries/{delivery_id}/status",
        json={"status": "DELIVERED"}
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_get_delivery(
    client: AsyncClient,
    sample_delivery_data
):
    """Test get delivery by ID"""
    # Create delivery
    response = await client.post("/v1/deliveries", json=sample_delivery_data)
    delivery_id = response.json()["id"]
    
    # Get delivery
    response = await client.get(f"/v1/deliveries/{delivery_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == delivery_id
    assert data["order_id"] == sample_delivery_data["order_id"]


@pytest.mark.asyncio
async def test_get_delivery_by_order(
    client: AsyncClient,
    sample_delivery_data
):
    """Test get delivery by order ID"""
    # Create delivery
    response = await client.post("/v1/deliveries", json=sample_delivery_data)
    order_id = sample_delivery_data["order_id"]
    
    # Get by order ID
    response = await client.get(f"/v1/deliveries/order/{order_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["order_id"] == order_id


@pytest.mark.asyncio
async def test_list_deliveries(
    client: AsyncClient,
    sample_delivery_data
):
    """Test list deliveries with filters"""
    # Create multiple deliveries
    await client.post("/v1/deliveries", json=sample_delivery_data)
    
    data2 = sample_delivery_data.copy()
    data2["order_id"] = str(uuid.uuid4())
    await client.post("/v1/deliveries", json=data2)
    
    # List all
    response = await client.get("/v1/deliveries")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    
    # Filter by status
    response = await client.get("/v1/deliveries?status=PENDING")
    assert response.status_code == 200
    data = response.json()
    assert all(d["status"] == "PENDING" for d in data)


@pytest.mark.asyncio
async def test_get_delivery_tracking(
    client: AsyncClient,
    db_session: AsyncSession,
    sample_delivery_partner,
    sample_delivery_data
):
    """Test get delivery tracking history"""
    # Create and update delivery
    response = await client.post("/v1/deliveries", json=sample_delivery_data)
    delivery_id = response.json()["id"]
    
    # Assign
    await client.post(
        f"/v1/deliveries/{delivery_id}/assign",
        json={}
    )
    
    # Update status
    await client.patch(
        f"/v1/deliveries/{delivery_id}/status",
        json={"status": "PICKED_UP"}
    )
    
    # Get tracking
    response = await client.get(f"/v1/deliveries/{delivery_id}/tracking")
    assert response.status_code == 200
    tracking = response.json()
    assert len(tracking) >= 3  # Created, Assigned, Picked up
    assert tracking[0]["event_type"] == "DELIVERY_CREATED"


@pytest.mark.asyncio
async def test_find_nearby_partners(
    client: AsyncClient,
    sample_delivery_partner
):
    """Test find nearby delivery partners"""
    response = await client.get(
        "/v1/partners/nearby?lat=12.9716&lng=77.5946"
    )
    assert response.status_code == 200
    partners = response.json()
    assert len(partners) >= 1
    assert partners[0]["id"] == str(sample_delivery_partner.id)


@pytest.mark.asyncio
async def test_update_partner_location(
    client: AsyncClient,
    sample_delivery_partner
):
    """Test update partner location"""
    new_location = {"lat": 12.9800, "lng": 77.6000}
    
    response = await client.patch(
        f"/v1/partners/{sample_delivery_partner.id}/location",
        json={"location": new_location}
    )
    assert response.status_code == 200
    
    # Verify location updated
    response = await client.get(f"/v1/partners/{sample_delivery_partner.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["current_location"]["lat"] == new_location["lat"]
    assert data["current_location"]["lng"] == new_location["lng"]


@pytest.mark.asyncio
async def test_update_partner_status(
    client: AsyncClient,
    sample_delivery_partner
):
    """Test update partner status"""
    response = await client.patch(
        f"/v1/partners/{sample_delivery_partner.id}/status",
        json={"status": "OFFLINE"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "OFFLINE"


@pytest.mark.asyncio
async def test_distance_calculation(db_session: AsyncSession):
    """Test distance calculation"""
    service = DeliveryService(db_session)
    
    # Bangalore to nearby location
    loc1 = {"lat": 12.9716, "lng": 77.5946}
    loc2 = {"lat": 12.9352, "lng": 77.6245}
    
    distance = service._calculate_distance(loc1, loc2)
    assert distance > 0
    assert distance < 10  # Should be within 10km


@pytest.mark.asyncio
async def test_delivery_fee_calculation(db_session: AsyncSession):
    """Test delivery fee calculation"""
    service = DeliveryService(db_session)
    
    # Base fee for short distance
    fee1 = service._calculate_delivery_fee(1.0)
    assert fee1 == 20.0  # Base fee
    
    # Fee for longer distance
    fee2 = service._calculate_delivery_fee(5.0)
    assert fee2 > 20.0  # Base + distance fee


@pytest.mark.asyncio
async def test_eta_calculation(db_session: AsyncSession):
    """Test ETA calculation"""
    service = DeliveryService(db_session)
    
    # 10 km at 20 km/h = 30 minutes
    eta = service._calculate_eta(10.0)
    assert eta == 30.0


@pytest.mark.asyncio
async def test_no_available_partners(
    client: AsyncClient,
    sample_delivery_data,
    db_session: AsyncSession,
    sample_delivery_partner
):
    """Test assignment when no partners available"""
    # Mark partner as busy
    sample_delivery_partner.status = "BUSY"
    await db_session.commit()
    
    # Create delivery
    response = await client.post("/v1/deliveries", json=sample_delivery_data)
    delivery_id = response.json()["id"]
    
    # Try to assign
    response = await client.post(
        f"/v1/deliveries/{delivery_id}/assign",
        json={}
    )
    assert response.status_code == 400
    assert "No available delivery partners" in response.json()["detail"]
