"""Tests for Payment Service"""
import pytest
from decimal import Decimal
import uuid


@pytest.mark.anyio
async def test_initiate_payment_razorpay(client, sample_customer_id, sample_order_id):
    """Test initiating a Razorpay payment"""
    response = await client.post(
        "/v1/payments/initiate",
        json={
            "order_id": str(sample_order_id),
            "customer_id": str(sample_customer_id),
            "amount": 1000.50,
            "payment_method": "UPI",
            "payment_gateway": "RAZORPAY",
            "customer_email": "customer@example.com",
            "customer_phone": "9876543210",
            "description": "Test payment"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "payment_id" in data["data"]
    assert "gateway_order_id" in data["data"]
    assert data["data"]["status"] == "PENDING"
    assert float(data["data"]["amount"]) == 1000.50


@pytest.mark.anyio
async def test_initiate_payment_cod(client, sample_customer_id, sample_order_id):
    """Test initiating a COD payment"""
    response = await client.post(
        "/v1/payments/initiate",
        json={
            "order_id": str(sample_order_id),
            "customer_id": str(sample_customer_id),
            "amount": 500.00,
            "payment_method": "COD",
            "customer_phone": "9876543210"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["status"] == "PENDING"
    assert "COD-" in data["data"]["gateway_order_id"]


@pytest.mark.anyio
async def test_initiate_payment_invalid_amount(client, sample_customer_id, sample_order_id):
    """Test initiating payment with invalid amount"""
    response = await client.post(
        "/v1/payments/initiate",
        json={
            "order_id": str(sample_order_id),
            "customer_id": str(sample_customer_id),
            "amount": 0,
            "payment_method": "UPI"
        }
    )
    
    assert response.status_code == 422  # Validation error


@pytest.mark.anyio
async def test_initiate_payment_duplicate_order(client, sample_customer_id, sample_order_id):
    """Test initiating payment for same order twice"""
    # First payment
    response1 = await client.post(
        "/v1/payments/initiate",
        json={
            "order_id": str(sample_order_id),
            "customer_id": str(sample_customer_id),
            "amount": 1000.00,
            "payment_method": "UPI"
        }
    )
    assert response1.status_code == 200
    
    # Second payment for same order
    response2 = await client.post(
        "/v1/payments/initiate",
        json={
            "order_id": str(sample_order_id),
            "customer_id": str(sample_customer_id),
            "amount": 1000.00,
            "payment_method": "UPI"
        }
    )
    assert response2.status_code == 200
    # Should return the existing payment
    assert response1.json()["data"]["payment_id"] == response2.json()["data"]["payment_id"]


@pytest.mark.anyio
async def test_get_payment(client, sample_customer_id, sample_order_id):
    """Test retrieving payment by ID"""
    # Create payment
    create_response = await client.post(
        "/v1/payments/initiate",
        json={
            "order_id": str(sample_order_id),
            "customer_id": str(sample_customer_id),
            "amount": 750.00,
            "payment_method": "CARD"
        }
    )
    payment_id = create_response.json()["data"]["payment_id"]
    
    # Get payment
    response = await client.get(f"/v1/payments/{payment_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert str(data["data"]["id"]) == payment_id
    assert data["data"]["payment_method"] == "CARD"


@pytest.mark.anyio
async def test_get_payment_not_found(client):
    """Test retrieving non-existent payment"""
    fake_id = str(uuid.uuid4())
    response = await client.get(f"/v1/payments/{fake_id}")
    
    assert response.status_code == 404


@pytest.mark.anyio
async def test_get_payment_by_order(client, sample_customer_id, sample_order_id):
    """Test retrieving payment by order ID"""
    # Create payment
    await client.post(
        "/v1/payments/initiate",
        json={
            "order_id": str(sample_order_id),
            "customer_id": str(sample_customer_id),
            "amount": 500.00,
            "payment_method": "UPI"
        }
    )
    
    # Get payment by order
    response = await client.get(f"/v1/payments/order/{sample_order_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert str(data["data"]["order_id"]) == str(sample_order_id)


@pytest.mark.anyio
async def test_list_payments(client, sample_customer_id):
    """Test listing payments"""
    # Create multiple payments
    for i in range(3):
        await client.post(
            "/v1/payments/initiate",
            json={
                "order_id": str(uuid.uuid4()),
                "customer_id": str(sample_customer_id),
                "amount": 100.00 * (i + 1),
                "payment_method": "UPI"
            }
        )
    
    # List all payments for customer
    response = await client.get(
        "/v1/payments",
        params={"customer_id": str(sample_customer_id)}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]) >= 3


@pytest.mark.anyio
async def test_list_payments_with_status_filter(client, sample_customer_id):
    """Test listing payments with status filter"""
    # Create payment
    await client.post(
        "/v1/payments/initiate",
        json={
            "order_id": str(uuid.uuid4()),
            "customer_id": str(sample_customer_id),
            "amount": 200.00,
            "payment_method": "UPI"
        }
    )
    
    # List payments with PENDING status
    response = await client.get(
        "/v1/payments",
        params={"customer_id": str(sample_customer_id), "status": "PENDING"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert all(p["status"] == "PENDING" for p in data["data"])


@pytest.mark.anyio
async def test_list_payments_pagination(client, sample_customer_id):
    """Test payment listing pagination"""
    # Create multiple payments
    for i in range(5):
        await client.post(
            "/v1/payments/initiate",
            json={
                "order_id": str(uuid.uuid4()),
                "customer_id": str(sample_customer_id),
                "amount": 100.00,
                "payment_method": "UPI"
            }
        )
    
    # Get first page
    response1 = await client.get(
        "/v1/payments",
        params={"customer_id": str(sample_customer_id), "limit": 2}
    )
    assert response1.status_code == 200
    assert len(response1.json()["data"]) == 2
    
    # Get second page
    response2 = await client.get(
        "/v1/payments",
        params={"customer_id": str(sample_customer_id), "skip": 2, "limit": 2}
    )
    assert response2.status_code == 200
    assert len(response2.json()["data"]) == 2


@pytest.mark.anyio
async def test_verify_razorpay_payment(client, sample_customer_id, sample_order_id, db_session):
    """Test verifying Razorpay payment"""
    # Create payment
    create_response = await client.post(
        "/v1/payments/initiate",
        json={
            "order_id": str(sample_order_id),
            "customer_id": str(sample_customer_id),
            "amount": 1500.00,
            "payment_method": "UPI",
            "payment_gateway": "RAZORPAY"
        }
    )
    gateway_order_id = create_response.json()["data"]["gateway_order_id"]
    
    # Mock Razorpay verification (signature validation skipped in test mode)
    response = await client.post(
        "/v1/payments/verify",
        json={
            "razorpay_order_id": gateway_order_id,
            "razorpay_payment_id": "pay_mock_123456",
            "razorpay_signature": "mock_signature_abc123"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["status"] == "SUCCESS"
    assert data["data"]["gateway_payment_id"] == "pay_mock_123456"


@pytest.mark.anyio
async def test_verify_payment_not_found(client):
    """Test verifying non-existent payment"""
    response = await client.post(
        "/v1/payments/verify",
        json={
            "razorpay_order_id": "order_fake_123",
            "razorpay_payment_id": "pay_fake_456",
            "razorpay_signature": "fake_signature"
        }
    )
    
    assert response.status_code == 400


@pytest.mark.anyio
async def test_get_payment_logs(client, sample_customer_id, sample_order_id):
    """Test retrieving payment logs"""
    # Create payment
    create_response = await client.post(
        "/v1/payments/initiate",
        json={
            "order_id": str(sample_order_id),
            "customer_id": str(sample_customer_id),
            "amount": 800.00,
            "payment_method": "UPI"
        }
    )
    payment_id = create_response.json()["data"]["payment_id"]
    
    # Get logs
    response = await client.get(f"/v1/payments/{payment_id}/logs")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]) >= 1  # At least PAYMENT_CREATED log
    assert data["data"][0]["event_type"] == "PAYMENT_CREATED"


@pytest.mark.anyio
async def test_razorpay_webhook(client, sample_customer_id, sample_order_id):
    """Test Razorpay webhook handling"""
    # Create payment
    create_response = await client.post(
        "/v1/payments/initiate",
        json={
            "order_id": str(sample_order_id),
            "customer_id": str(sample_customer_id),
            "amount": 1200.00,
            "payment_method": "UPI",
            "payment_gateway": "RAZORPAY"
        }
    )
    gateway_order_id = create_response.json()["data"]["gateway_order_id"]
    
    # Send webhook
    webhook_payload = {
        "entity": "event",
        "account_id": "acc_123456",
        "event": "payment.captured",
        "contains": ["payment"],
        "payload": {
            "payment": {
                "entity": {
                    "id": "pay_webhook_789",
                    "order_id": gateway_order_id,
                    "amount": 120000,
                    "currency": "INR",
                    "status": "captured"
                }
            }
        },
        "created_at": 1234567890
    }
    
    response = await client.post(
        "/v1/payments/webhooks/razorpay",
        json=webhook_payload,
        headers={"X-Razorpay-Signature": "mock_signature"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


@pytest.mark.anyio
async def test_cashfree_webhook(client):
    """Test Cashfree webhook handling"""
    webhook_payload = {
        "type": "PAYMENT_SUCCESS",
        "data": {
            "order_id": "cf_order_123",
            "payment_id": "cf_pay_456",
            "amount": 500.00
        }
    }
    
    response = await client.post(
        "/v1/payments/webhooks/cashfree",
        json=webhook_payload
    )
    
    assert response.status_code == 200
