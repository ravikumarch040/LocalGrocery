#!/usr/bin/env python
"""Test multiple product creation"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import httpx
import json
import asyncio

async def test_multiple_products():
    category_id = "c23ee86e-bf27-426d-b3c9-5dc591f97c0b"
    
    products_to_create = [
        {
            "name": "Full Cream Milk",
            "description": "Fresh pasteurized full cream milk",
            "base_price": "65.00",
            "unit": "liter"
        },
        {
            "name": "Brown Bread - Multigrain",
            "description": "Healthy multigrain bread",
            "base_price": "45.00",
            "unit": "piece"
        },
        {
            "name": "Orange Juice - Fresh",
            "description": "Fresh orange juice",
            "base_price": "120.00",
            "unit": "liter"
        }
    ]
    
    async with httpx.AsyncClient() as client:
        for product in products_to_create:
            payload = {
                **product,
                "category_id": category_id,
                "is_active": True
            }
            response = await client.post(
                "http://localhost:8002/api/v1/products/",
                json=payload
            )
            if response.status_code == 201:
                resp_json = response.json()
                print(f"✅ Created: {resp_json['name']} (ID: {resp_json['id']})")
                print(f"   Category: {resp_json['category']['name']}")
            else:
                print(f"❌ Failed: {product['name']} - {response.status_code}")
                print(f"   Error: {response.text}")

asyncio.run(test_multiple_products())
