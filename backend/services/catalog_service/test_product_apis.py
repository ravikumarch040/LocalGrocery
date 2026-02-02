#!/usr/bin/env python
"""Test script to get category ID and test product creation"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import asyncio
import os
import json
from decimal import Decimal

os.environ['DATABASE_URL'] = 'postgresql+asyncpg://localgrocery:dev_password_change_in_prod@localhost/localgrocery'

from app.database import AsyncSessionLocal
from sqlalchemy import select
from app.models import Category
import httpx

async def get_category():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Category).where(Category.parent_id == None).limit(1))
        cat = result.scalar_one_or_none()
        if cat:
            return str(cat.id)
    return None

async def test_create_product():
    category_id = await get_category()
    if not category_id:
        print("ERROR: No categories found!")
        return
    
    print(f"Using Category ID: {category_id}")
    
    payload = {
        "name": "Organic Apples - Fresh",
        "description": "Fresh organic apples from local farms",
        "category_id": category_id,
        "base_price": "150.00",
        "unit": "kg",
        "image_url": "https://example.com/apple.jpg",
        "variants": [
            {"size": "500g", "price": "75"},
            {"size": "1kg", "price": "150"}
        ],
        "is_active": True
    }
    
    print(f"Payload: {json.dumps(payload, indent=2, default=str)}")
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8002/api/v1/products/",
            json=payload
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")

asyncio.run(test_create_product())
