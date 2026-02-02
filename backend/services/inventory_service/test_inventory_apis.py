#!/usr/bin/env python
"""Inventory Service API Integration Tests"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import httpx
import asyncio
import pytest
from uuid import uuid4

BASE_URL = "http://localhost:8007"
STORE_ID = str(uuid4())
PRODUCT_ID = str(uuid4())

@pytest.mark.asyncio
async def test_inventory_apis():
    """Test all Inventory Service APIs"""
    
    print("\n" + "="*70)
    print("INVENTORY SERVICE - API TEST SUITE")
    print("="*70)
    
    async with httpx.AsyncClient() as client:
        
        # Test 1: Health Check
        print("\n" + "-"*70)
        print("[1] HEALTH CHECK")
        print("-"*70)
        
        try:
            response = await client.get(f"{BASE_URL}/health", timeout=5.0)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ {data['status']} - {data['service']}")
            else:
                print(f"   ❌ Failed: {response.text}")
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            return
        
        # Test 2: Create Inventory
        print("\n" + "-"*70)
        print("[2] CREATE INVENTORY (POST /v1/inventory)")
        print("-"*70)
        
        create_payload = {
            "store_id": STORE_ID,
            "product_id": PRODUCT_ID,
            "stock_qty": 100,
            "cost_price": 50.0,
            "selling_price": 100.0,
            "reorder_level": 10,
            "reorder_qty": 50
        }
        
        print(f"   Creating inventory: Store={STORE_ID[:8]}..., Product={PRODUCT_ID[:8]}...")
        
        try:
            response = await client.post(
                f"{BASE_URL}/v1/inventory",
                json=create_payload,
                timeout=10.0
            )
            
            print(f"   Status: {response.status_code}")
            if response.status_code == 201:
                data = response.json()
                print(f"   ✅ Created!")
                print(f"      - Stock: {data['stock_qty']}")
                print(f"      - Available: {data['available_qty']}")
                print(f"      - Reserved: {data['reserved_qty']}")
                print(f"      - Status: {data['status']}")
                print(f"      - Price: ₹{data['selling_price']}")
            else:
                print(f"   ❌ Failed: {response.text}")
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
        
        # Test 3: Get Inventory
        print("\n" + "-"*70)
        print("[3] GET INVENTORY (GET /v1/inventory/{store_id}/{product_id})")
        print("-"*70)
        
        try:
            response = await client.get(
                f"{BASE_URL}/v1/inventory/{STORE_ID}/{PRODUCT_ID}",
                timeout=10.0
            )
            
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Retrieved!")
                print(f"      - Stock: {data['stock_qty']}")
                print(f"      - Available: {data['available_qty']}")
                print(f"      - Status: {data['status']}")
            else:
                print(f"   ❌ Failed: {response.text}")
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
        
        # Test 4: Check Availability
        print("\n" + "-"*70)
        print("[4] CHECK AVAILABILITY (POST /v1/inventory/check-availability)")
        print("-"*70)
        
        availability_payload = {
            "items": [
                {
                    "store_id": STORE_ID,
                    "product_id": PRODUCT_ID,
                    "quantity": 5
                }
            ]
        }
        
        try:
            response = await client.post(
                f"{BASE_URL}/v1/inventory/check-availability",
                json=availability_payload,
                timeout=10.0
            )
            
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Available: {data['all_available']}")
                if data.get('items'):
                    for item in data['items']:
                        print(f"      - Product: {item['product_id'][:8]}... In Stock: {item['in_stock']}, Qty: {item.get('available_qty', 'N/A')}")
            else:
                print(f"   ❌ Failed: {response.text}")
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
        
        # Test 5: Adjust Stock
        print("\n" + "-"*70)
        print("[5] ADJUST STOCK (POST /v1/inventory/{store_id}/{product_id}/adjust)")
        print("-"*70)
        
        adjust_payload = {
            "qty_change": 50,
            "source": "restock",
            "user_id": str(uuid4()),
            "notes": "Manual restock"
        }
        
        try:
            response = await client.post(
                f"{BASE_URL}/v1/inventory/{STORE_ID}/{PRODUCT_ID}/adjust",
                json=adjust_payload,
                timeout=10.0
            )
            
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Adjusted!")
                print(f"      - New Stock: {data['stock_qty']}")
                print(f"      - Available: {data['available_qty']}")
            else:
                print(f"   ❌ Failed: {response.text}")
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
        
        # Test 6: Reserve Inventory
        print("\n" + "-"*70)
        print("[6] RESERVE INVENTORY (POST /v1/reservations)")
        print("-"*70)
        
        order_id = str(uuid4())
        reserve_payload = {
            "order_id": order_id,
            "customer_id": str(uuid4()),
            "items": [
                {
                    "store_id": STORE_ID,
                    "product_id": PRODUCT_ID,
                    "qty": 10
                }
            ]
        }
        
        try:
            response = await client.post(
                f"{BASE_URL}/v1/reservations",
                json=reserve_payload,
                timeout=10.0
            )
            
            print(f"   Status: {response.status_code}")
            if response.status_code == 201:
                data = response.json()
                print(f"   ✅ Reserved!")
                print(f"      - Reservation ID: {data['reservation_id']}")
                print(f"      - Order ID: {data['order_id']}")
                print(f"      - Status: {data['status']}")
                print(f"      - Items: {len(data.get('items', []))}")
                print(f"      - Expires At: {data.get('expires_at', 'N/A')}")
            else:
                print(f"   ❌ Failed: {response.text}")
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
        
        # Test 7: Confirm Reservation
        print("\n" + "-"*70)
        print("[7] CONFIRM RESERVATION (POST /v1/reservations/{order_id}/confirm)")
        print("-"*70)
        
        confirm_payload = {
            "reason": "Payment successful"
        }
        
        try:
            response = await client.post(
                f"{BASE_URL}/v1/reservations/{order_id}/confirm",
                json=confirm_payload,
                timeout=10.0
            )
            
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Confirmed!")
                print(f"      - Status: {data['status']}")
                print(f"      - Items Confirmed: {len(data.get('items', []))}")
            else:
                print(f"   ❌ Failed: {response.text}")
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
        
        # Test 8: Get Audit Logs
        print("\n" + "-"*70)
        print("[8] GET AUDIT LOGS (GET /v1/audit-logs/{inventory_id})")
        print("-"*70)
        
        try:
            response = await client.get(
                f"{BASE_URL}/v1/audit-logs/{PRODUCT_ID}",
                timeout=10.0
            )
            
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Retrieved!")
                print(f"      - Total Logs: {data['count']}")
                if data['data']:
                    print(f"      - Latest: {data['data'][0]['source']} - {data['data'][0]['qty_changed']} units")
            else:
                print(f"   ❌ Failed: {response.text}")
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
    
    print("\n" + "="*70)
    print("INVENTORY SERVICE API TESTS COMPLETED")
    print("="*70 + "\n")

asyncio.run(test_inventory_apis())
