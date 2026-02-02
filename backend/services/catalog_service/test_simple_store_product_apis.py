#!/usr/bin/env python
"""Simple test for all 5 Store Product APIs"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import httpx
import json
import asyncio
from uuid import uuid4

async def test():
    async with httpx.AsyncClient() as client:
        store_id = str(uuid4())
        product_id = "b43c04e9-7ef6-4b98-b3f8-6564901118a0"
        
        print("\n=== STORE PRODUCT API TEST ===\n")
        
        # 1. CREATE
        print("[1] CREATE - POST /api/v1/store-products/")
        create_payload = {
            "store_id": store_id,
            "product_id": product_id,
            "stock_quantity": 100,
            "store_price": "299.99",
            "is_available": True
        }
        create_resp = await client.post(
            "http://localhost:8002/api/v1/store-products/",
            json=create_payload
        )
        print(f"   Status: {create_resp.status_code}")
        create_data = create_resp.json()
        store_product_id = create_data.get('id')
        has_product = create_data.get('product') is not None
        has_category = create_data.get('product', {}).get('category') is not None
        print(f"   Product loaded: {has_product}, Category loaded: {has_category}")
        if create_resp.status_code != 201:
            print(f"   ERROR: {create_data}")
        else:
            print(f"   SUCCESS - ID: {store_product_id}\n")
        
        # 2. READ
        print("[2] READ - GET /api/v1/store-products/{id}")
        read_resp = await client.get(
            f"http://localhost:8002/api/v1/store-products/{store_product_id}"
        )
        print(f"   Status: {read_resp.status_code}")
        read_data = read_resp.json()
        has_product = read_data.get('product') is not None
        has_category = read_data.get('product', {}).get('category') is not None
        print(f"   Product loaded: {has_product}, Category loaded: {has_category}")
        if read_resp.status_code != 200:
            print(f"   ERROR: {read_data}")
        else:
            print(f"   SUCCESS\n")
        
        # 3. UPDATE
        print("[3] UPDATE - PUT /api/v1/store-products/{id}")
        print(f"   Updating store_product_id: {store_product_id}")
        update_payload = {
            "stock_quantity": 150,
            "store_price": "289.99",
            "is_available": True
        }
        update_resp = await client.put(
            f"http://localhost:8002/api/v1/store-products/{store_product_id}",
            json=update_payload
        )
        print(f"   Status: {update_resp.status_code}")
        print(f"   Response content: {update_resp.text[:500]}")
        if update_resp.status_code != 200:
            try:
                update_data = update_resp.json()
                print(f"   ERROR: {update_data}")
            except:
                print(f"   ERROR: Invalid JSON response")
        else:
            update_data = update_resp.json()
            print(f"   Stock updated to: {update_data.get('stock_quantity')}")
            print(f"   Price updated to: {update_data.get('store_price')}")
            print(f"   SUCCESS\n")
        
        # 4. LIST
        print("[4] LIST - GET /api/v1/store-products/store/{store_id}")
        list_resp = await client.get(
            f"http://localhost:8002/api/v1/store-products/store/{store_id}?is_available=true&page=1&page_size=10"
        )
        print(f"   Status: {list_resp.status_code}")
        if list_resp.status_code != 200:
            list_data = list_resp.json()
            print(f"   ERROR: {list_data}")
        else:
            list_data = list_resp.json()
            # LIST returns plain list, not wrapped in dict
            products_in_response = list_data if isinstance(list_data, list) else list_data.get('data', [])
            print(f"   Products found: {len(products_in_response)}")
            if products_in_response:
                has_product = products_in_response[0].get('product') is not None
                has_category = products_in_response[0].get('product', {}).get('category') is not None
                print(f"   Product loaded: {has_product}, Category loaded: {has_category}")
            print(f"   SUCCESS\n")
        
        # 5. DELETE
        print("[5] DELETE - DELETE /api/v1/store-products/{id}")
        delete_resp = await client.delete(
            f"http://localhost:8002/api/v1/store-products/{store_product_id}"
        )
        print(f"   Status: {delete_resp.status_code}")
        if delete_resp.status_code != 200:
            delete_data = delete_resp.json()
            print(f"   ERROR: {delete_data}")
        else:
            print(f"   SUCCESS - Product marked as unavailable\n")
        
        print("=== TEST COMPLETE ===\n")

asyncio.run(test())
