#!/usr/bin/env python
"""Comprehensive Store Product API Tests"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import httpx
import json
import asyncio
from uuid import uuid4

# Test UUIDs and data
STORE_ID = str(uuid4())
PRODUCT_IDS = []

async def test_store_product_apis():
    """Test all 5 Store Product APIs"""
    
    print("\n" + "="*70)
    print("CATALOG SERVICE - STORE PRODUCT API TEST")
    print("="*70)
    
    async with httpx.AsyncClient() as client:
        # First, get a product ID
        print("\n📦 Getting a product from the system...")
        products_response = await client.get("http://localhost:8002/api/v1/products/?limit=1")
        if products_response.status_code == 200:
            products_data = products_response.json()
            if products_data['products']:
                PRODUCT_IDS.append(products_data['products'][0]['id'])
                print(f"   ✅ Using product: {products_data['products'][0]['name']}")
                print(f"   📝 Product ID: {PRODUCT_IDS[0]}")
                print(f"   🏪 Store ID: {STORE_ID}")
        
        if not PRODUCT_IDS:
            print("❌ No products found!")
            return
        
        product_id = PRODUCT_IDS[0]
        store_product_id = None
        
        # ============================================================
        # 1️⃣  CREATE - Add product to store
        # ============================================================
        print("\n" + "-"*70)
        print("1️⃣  CREATE - Add Product to Store (POST /store-products/)")
        print("-"*70)
        
        create_payload = {
            "store_id": STORE_ID,
            "product_id": product_id,
            "stock_quantity": 100,
            "store_price": "299.99",
            "is_available": True
        }
        
        print(f"   📨 Payload: {json.dumps(create_payload, indent=6)}")
        response = await client.post(
            "http://localhost:8002/api/v1/store-products/",
            json=create_payload
        )
        
        print(f"   📊 Status: {response.status_code}")
        if response.status_code == 201:
            data = response.json()
            print(f"   Full Response: {json.dumps(data, indent=6, default=str)}")
            store_product_id = data['id']
            print(f"   ✅ Successfully created!")
            print(f"      - ID: {store_product_id}")
            print(f"      - Store ID: {data['store_id']}")
            if data.get('product'):
                print(f"      - Product: {data.get('product', {}).get('name', 'N/A')}")
            else:
                print(f"      - Product: NOT LOADED (null)")
            print(f"      - Stock: {data['stock_quantity']} units")
            print(f"      - Store Price: ₹{data['store_price']}")
            print(f"      - Available: {data['is_available']}")
        else:
            print(f"   ❌ Failed!")
            print(f"   Error: {response.text}")
            return
        
        # ============================================================
        # 2️⃣  READ - Get store product details
        # ============================================================
        print("\n" + "-"*70)
        print("2️⃣  READ - Get Store Product (GET /store-products/{id})")
        print("-"*70)
        
        response = await client.get(f"http://localhost:8002/api/v1/store-products/{store_product_id}")
        
        print(f"   📊 Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Successfully retrieved!")
            print(f"      - Product Name: {data.get('product', {}).get('name', 'N/A')}")
            print(f"      - Category: {data.get('product', {}).get('category', {}).get('name', 'N/A')}")
            print(f"      - Stock: {data['stock_quantity']} units")
            print(f"      - Price: ₹{data['store_price']}")
            print(f"      - Available: {data['is_available']}")
        else:
            print(f"   ❌ Failed!")
            print(f"   Error: {response.text}")
        
        # ============================================================
        # 3️⃣  UPDATE - Update store product (stock, price)
        # ============================================================
        print("\n" + "-"*70)
        print("3️⃣  UPDATE - Update Store Product (PUT /store-products/{id})")
        print("-"*70)
        
        update_payload = {
            "stock_quantity": 150,
            "store_price": "289.99",
            "is_available": True
        }
        
        print(f"   📨 Update Payload: {json.dumps(update_payload, indent=6)}")
        response = await client.put(
            f"http://localhost:8002/api/v1/store-products/{store_product_id}",
            json=update_payload
        )
        
        print(f"   📊 Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Successfully updated!")
            print(f"      - Stock: {data['stock_quantity']} units (was 100)")
            print(f"      - Price: ₹{data['store_price']} (was ₹299.99)")
        else:
            print(f"   ❌ Failed!")
            print(f"   Error: {response.text}")
        
        # ============================================================
        # 4️⃣  LIST - Get all products in store
        # ============================================================
        print("\n" + "-"*70)
        print("4️⃣  LIST - Get Store Products (GET /store-products/store/{store_id})")
        print("-"*70)
        
        response = await client.get(
            f"http://localhost:8002/api/v1/store-products/store/{STORE_ID}?is_available=true&page=1&page_size=10"
        )
        
        print(f"   📊 Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                print(f"   ✅ Successfully retrieved!")
                print(f"      - Total Products: {len(data)}")
                for idx, sp in enumerate(data[:3], 1):
                    print(f"      {idx}. {sp['product']['name']}")
                    print(f"         Stock: {sp['stock_quantity']}, Price: ₹{sp['store_price']}")
            else:
                print(f"   Response type: {type(data)}")
                print(f"   Data: {json.dumps(data, indent=6, default=str)}")
        else:
            print(f"   ❌ Failed!")
            print(f"   Error: {response.text}")
        
        # ============================================================
        # 5️⃣  DELETE - Remove product from store
        # ============================================================
        print("\n" + "-"*70)
        print("5️⃣  DELETE - Remove Product from Store (DELETE /store-products/{id})")
        print("-"*70)
        
        response = await client.delete(
            f"http://localhost:8002/api/v1/store-products/{store_product_id}"
        )
        
        print(f"   📊 Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Successfully deleted!")
            print(f"      - Message: {data.get('message', 'Product removed from store')}")
        else:
            print(f"   ❌ Failed!")
            print(f"   Error: {response.text}")
        
        # Verify deletion
        print("\n   🔍 Verifying deletion...")
        response = await client.get(f"http://localhost:8002/api/v1/store-products/{store_product_id}")
        if response.status_code == 404:
            print(f"   ✅ Confirmed - Product is no longer available in store")
        else:
            print(f"   ⚠️  Product still exists (soft delete): Status {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"      Available: {data['is_available']}")
    
    print("\n" + "="*70)
    print("✅ ALL STORE PRODUCT API TESTS COMPLETED")
    print("="*70 + "\n")

asyncio.run(test_store_product_apis())
