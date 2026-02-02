#!/usr/bin/env python
"""Comprehensive Order Service API Tests"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import httpx
import json
import asyncio
from uuid import uuid4
from datetime import datetime

# Test data
TEST_CUSTOMER_ID = str(uuid4())
TEST_STORE_ID = str(uuid4())
PRODUCT_ID = "b43c04e9-7ef6-4b98-b3f8-6564901118a0"  # From catalog service


async def test_order_apis():
    """Test all Order Service APIs"""
    
    print("\n" + "="*70)
    print("ORDER SERVICE - API TEST SUITE")
    print("="*70)
    
    async with httpx.AsyncClient() as client:
        order_id = None
        
        # ============================================================
        # 1️⃣  CREATE - Create a new order
        # ============================================================
        print("\n" + "-"*70)
        print("1️⃣  CREATE - Create Order (POST /api/v1/orders/)")
        print("-"*70)
        
        create_payload = {
            "customer_id": TEST_CUSTOMER_ID,
            "store_id": TEST_STORE_ID,
            "payment_method": "UPI",
            "delivery_address": {
                "street": "123 Main Street",
                "city": "Bangalore",
                "pincode": "560001",
                "state": "Karnataka",
                "country": "India"
            },
            "notes": "Please deliver between 2-4 PM",
            "items": [
                {
                    "product_id": PRODUCT_ID,
                    "product_name": "Premium Basmati Rice",
                    "quantity": 2,
                    "unit_price": "280.00",
                    "variant_data": {"size": "1kg"}
                }
            ]
        }
        
        print(f"   📨 Creating order with:")
        print(f"      - Customer: {TEST_CUSTOMER_ID}")
        print(f"      - Store: {TEST_STORE_ID}")
        print(f"      - Items: 1 product, 2 units")
        
        try:
            response = await client.post(
                "http://localhost:8003/api/v1/orders/",
                json=create_payload,
                timeout=10.0
            )
            
            print(f"   📊 Status: {response.status_code}")
            if response.status_code == 201:
                data = response.json()
                order_id = data['id']
                print(f"   ✅ Successfully created!")
                print(f"      - Order ID: {order_id}")
                print(f"      - Order Number: {data['order_number']}")
                print(f"      - Status: {data['status']}")
                print(f"      - Payment Status: {data['payment_status']}")
                print(f"      - Subtotal: ₹{data['subtotal']}")
                print(f"      - Tax: ₹{data['tax']}")
                print(f"      - Delivery Fee: ₹{data['delivery_fee']}")
                print(f"      - Total: ₹{data['total_amount']}")
                print(f"      - Items: {len(data['items'])}")
            else:
                print(f"   ❌ Failed!")
                print(f"   Response: {response.text}")
                return
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            return
        
        # ============================================================
        # 2️⃣  READ - Get order by ID
        # ============================================================
        print("\n" + "-"*70)
        print("2️⃣  READ - Get Order by ID (GET /api/v1/orders/{id})")
        print("-"*70)
        
        try:
            response = await client.get(
                f"http://localhost:8003/api/v1/orders/{order_id}",
                timeout=10.0
            )
            
            print(f"   📊 Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Successfully retrieved!")
                print(f"      - Order ID: {data['id']}")
                print(f"      - Order Number: {data['order_number']}")
                print(f"      - Status: {data['status']}")
                print(f"      - Items: {len(data['items'])}")
                for idx, item in enumerate(data['items'], 1):
                    print(f"        {idx}. {item['product_name']} x{item['quantity']} @ ₹{item['unit_price']}")
            else:
                print(f"   ❌ Failed!")
                print(f"   Response: {response.text}")
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
        
        # ============================================================
        # 3️⃣  READ BY ORDER NUMBER
        # ============================================================
        print("\n" + "-"*70)
        print("3️⃣  READ - Get Order by Order Number (GET /api/v1/orders/number/{number})")
        print("-"*70)
        
        try:
            # First get the order number
            response = await client.get(f"http://localhost:8003/api/v1/orders/{order_id}")
            if response.status_code == 200:
                order_number = response.json()['order_number']
                
                response = await client.get(
                    f"http://localhost:8003/api/v1/orders/number/{order_number}",
                    timeout=10.0
                )
                
                print(f"   📊 Status: {response.status_code}")
                if response.status_code == 200:
                    data = response.json()
                    print(f"   ✅ Successfully retrieved!")
                    print(f"      - Order Number: {data['order_number']}")
                    print(f"      - Status: {data['status']}")
                    print(f"      - Total Amount: ₹{data['total_amount']}")
                else:
                    print(f"   ❌ Failed!")
                    print(f"   Response: {response.text}")
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
        
        # ============================================================
        # 4️⃣  LIST - List all orders
        # ============================================================
        print("\n" + "-"*70)
        print("4️⃣  LIST - Get Orders (GET /api/v1/orders/)")
        print("-"*70)
        
        try:
            response = await client.get(
                f"http://localhost:8003/api/v1/orders/?page=1&page_size=10",
                timeout=10.0
            )
            
            print(f"   📊 Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Successfully retrieved!")
                print(f"      - Total Orders: {data['total']}")
                print(f"      - Page: {data['page']}")
                print(f"      - Page Size: {data['page_size']}")
                print(f"      - Orders Returned: {len(data['orders'])}")
                if data['orders']:
                    print(f"      - First Order: {data['orders'][0]['order_number']}")
            else:
                print(f"   ❌ Failed!")
                print(f"   Response: {response.text}")
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
        
        # ============================================================
        # 5️⃣  LIST WITH FILTERS
        # ============================================================
        print("\n" + "-"*70)
        print("5️⃣  LIST WITH FILTERS - Get Customer Orders (GET /api/v1/orders/?customer_id=...)")
        print("-"*70)
        
        try:
            response = await client.get(
                f"http://localhost:8003/api/v1/orders/?customer_id={TEST_CUSTOMER_ID}&page=1&page_size=10",
                timeout=10.0
            )
            
            print(f"   📊 Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Successfully retrieved!")
                print(f"      - Total Orders for Customer: {data['total']}")
                print(f"      - Orders Returned: {len(data['orders'])}")
                if data['orders']:
                    for idx, order in enumerate(data['orders'][:3], 1):
                        print(f"        {idx}. Order #{order['order_number']} - Status: {order['status']}")
            else:
                print(f"   ❌ Failed!")
                print(f"   Response: {response.text}")
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
        
        # ============================================================
        # 6️⃣  UPDATE - Update order status
        # ============================================================
        print("\n" + "-"*70)
        print("6️⃣  UPDATE - Update Order Status (PUT /api/v1/orders/{id})")
        print("-"*70)
        
        update_payload = {
            "status": "CONFIRMED"
        }
        
        print(f"   📨 Updating order status to: CONFIRMED")
        
        try:
            response = await client.put(
                f"http://localhost:8003/api/v1/orders/{order_id}",
                json=update_payload,
                timeout=10.0
            )
            
            print(f"   📊 Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Successfully updated!")
                print(f"      - New Status: {data['status']}")
                print(f"      - Confirmed At: {data.get('confirmed_at', 'N/A')}")
            else:
                print(f"   ❌ Failed!")
                print(f"   Response: {response.text}")
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
        
        # ============================================================
        # 7️⃣  UPDATE PAYMENT STATUS
        # ============================================================
        print("\n" + "-"*70)
        print("7️⃣  UPDATE - Update Payment Status (PUT /api/v1/orders/{id})")
        print("-"*70)
        
        update_payload = {
            "payment_status": "PAID"
        }
        
        print(f"   📨 Updating payment status to: PAID")
        
        try:
            response = await client.put(
                f"http://localhost:8003/api/v1/orders/{order_id}",
                json=update_payload,
                timeout=10.0
            )
            
            print(f"   📊 Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Successfully updated!")
                print(f"      - Payment Status: {data['payment_status']}")
            else:
                print(f"   ❌ Failed!")
                print(f"   Response: {response.text}")
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
        
        # ============================================================
        # 8️⃣  UPDATE TO DELIVERED
        # ============================================================
        print("\n" + "-"*70)
        print("8️⃣  UPDATE - Mark as Delivered (PUT /api/v1/orders/{id})")
        print("-"*70)
        
        update_payload = {
            "status": "DELIVERED"
        }
        
        print(f"   📨 Updating order status to: DELIVERED")
        
        try:
            response = await client.put(
                f"http://localhost:8003/api/v1/orders/{order_id}",
                json=update_payload,
                timeout=10.0
            )
            
            print(f"   📊 Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Successfully updated!")
                print(f"      - Status: {data['status']}")
                print(f"      - Delivered At: {data.get('delivered_at', 'N/A')}")
            else:
                print(f"   ❌ Failed!")
                print(f"   Response: {response.text}")
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
        
        # ============================================================
        # 9️⃣  CREATE ANOTHER ORDER TO TEST CANCEL
        # ============================================================
        print("\n" + "-"*70)
        print("9️⃣  CREATE - Create Another Order (for cancellation test)")
        print("-"*70)
        
        cancel_order_id = None
        
        create_payload['items'][0]['quantity'] = 1
        
        try:
            response = await client.post(
                "http://localhost:8003/api/v1/orders/",
                json=create_payload,
                timeout=10.0
            )
            
            print(f"   📊 Status: {response.status_code}")
            if response.status_code == 201:
                data = response.json()
                cancel_order_id = data['id']
                print(f"   ✅ Successfully created!")
                print(f"      - Order ID: {cancel_order_id}")
                print(f"      - Status: {data['status']}")
            else:
                print(f"   ❌ Failed!")
                print(f"   Response: {response.text}")
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
        
        # ============================================================
        # 🔟  DELETE - Cancel an order
        # ============================================================
        print("\n" + "-"*70)
        print("🔟  DELETE - Cancel Order (DELETE /api/v1/orders/{id})")
        print("-"*70)
        
        if cancel_order_id:
            try:
                response = await client.delete(
                    f"http://localhost:8003/api/v1/orders/{cancel_order_id}",
                    timeout=10.0
                )
                
                print(f"   📊 Status: {response.status_code}")
                if response.status_code == 200:
                    data = response.json()
                    print(f"   ✅ Successfully cancelled!")
                    print(f"      - Message: {data['message']}")
                    print(f"      - Order ID: {data['data']['order_id']}")
                else:
                    print(f"   ❌ Failed!")
                    print(f"   Response: {response.text}")
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
        
        # Verify cancellation
        print("\n   🔍 Verifying cancellation...")
        try:
            response = await client.get(f"http://localhost:8003/api/v1/orders/{cancel_order_id}")
            if response.status_code == 200:
                data = response.json()
                print(f"   ⚠️  Order still exists with status: {data['status']}")
            elif response.status_code == 404:
                print(f"   ✅ Confirmed - Order no longer available")
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
    
    print("\n" + "="*70)
    print("✅ ORDER SERVICE API TEST SUITE COMPLETED")
    print("="*70 + "\n")


if __name__ == "__main__":
    asyncio.run(test_order_apis())
