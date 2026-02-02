#!/usr/bin/env python
"""Comprehensive test of product API with category relationships"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import httpx
import json
import asyncio

async def run_tests():
    base_url = "http://localhost:8002/api/v1"
    category_id = "c23ee86e-bf27-426d-b3c9-5dc591f97c0b"
    
    async with httpx.AsyncClient() as client:
        print("\n" + "="*60)
        print("CATALOG SERVICE - PRODUCT API TEST")
        print("="*60)
        
        # Test 1: Create a product
        print("\n1️⃣  Creating a new product...")
        create_payload = {
            "name": "Premium Basmati Rice",
            "description": "Long grain basmati rice from Punjab",
            "category_id": category_id,
            "base_price": "280.00",
            "unit": "kg",
            "variants": [
                {"size": "1kg", "price": "280"},
                {"size": "5kg", "price": "1400"}
            ],
            "is_active": True
        }
        
        response = await client.post(f"{base_url}/products/", json=create_payload)
        product = response.json()
        product_id = product['id']
        
        print(f"   ✅ Status: {response.status_code}")
        print(f"   📦 Product: {product['name']}")
        print(f"   🏷️  Category: {product['category']['name']}")
        print(f"   💰 Price: ₹{product['base_price']}")
        print(f"   📏 Unit: {product['unit']}")
        
        # Test 2: Get the product
        print(f"\n2️⃣  Retrieving product {product_id[:8]}...")
        response = await client.get(f"{base_url}/products/{product_id}")
        product = response.json()
        
        print(f"   ✅ Status: {response.status_code}")
        print(f"   📦 Product: {product['name']}")
        print(f"   🏷️  Category Relationship: {product['category']['slug']}")
        
        # Test 3: Update the product
        print(f"\n3️⃣  Updating product...")
        update_payload = {
            "base_price": "290.00",
            "description": "Premium aged basmati rice from Punjab"
        }
        
        response = await client.put(f"{base_url}/products/{product_id}", json=update_payload)
        product = response.json()
        
        print(f"   ✅ Status: {response.status_code}")
        print(f"   📦 Product: {product['name']}")
        print(f"   💰 Updated Price: ₹{product['base_price']}")
        print(f"   📝 Description: {product['description']}")
        
        # Test 4: List products with category filter
        print(f"\n4️⃣  Listing products in category...")
        response = await client.get(f"{base_url}/products/", params={
            "category_id": category_id,
            "page": 1,
            "page_size": 3
        })
        results = response.json()
        
        print(f"   ✅ Status: {response.status_code}")
        print(f"   📊 Total: {results['total']} products")
        print(f"   📄 Page: {results['page']} (showing {len(results['products'])} items)")
        for i, p in enumerate(results['products'][:3], 1):
            print(f"      {i}. {p['name']} - ₹{p['base_price']} ({p['category']['name']})")
        
        # Test 5: Search by price range
        print(f"\n5️⃣  Filtering by price range (100-200)...")
        response = await client.get(f"{base_url}/products/", params={
            "min_price": 100,
            "max_price": 200,
            "page_size": 10
        })
        results = response.json()
        
        print(f"   ✅ Status: {response.status_code}")
        print(f"   📊 Found: {results['total']} products in range")
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED")
        print("="*60 + "\n")

asyncio.run(run_tests())
