# AsyncIO + SQLAlchemy ORM Serialization Pattern

## Problem Summary

When using FastAPI with SQLAlchemy async ORM, endpoints that return SQLAlchemy ORM objects encounter **greenlet errors** when Pydantic tries to serialize the response after the database session has closed.

### The Root Cause

FastAPI's dependency injection with `get_db` closes the `AsyncSession` immediately after the endpoint handler completes. SQLAlchemy marks all ORM objects as "expired" after a `commit()`. When Pydantic tries to serialize the response (which happens AFTER the endpoint returns), accessing any attribute on an expired ORM object triggers an async lazy-load attempt. This async load happens outside the async database context, causing:

```
greenlet_spawn has not been called; can't call await_only()
```

## The Solution: Dict-Based Serialization

**Serialize ORM objects to plain Python dicts WITHIN the service, while the database session is still active.** Return dicts from service methods instead of ORM objects.

### Why This Works

1. Dicts don't trigger lazy-loading
2. All data is already in memory
3. No attribute access after session closes
4. Dicts are JSON-serializable by default
5. FastAPI doesn't need to do anything - just returns the dict

## Implementation Pattern

### Service Method Structure

```python
async def update_store_product(
    self,
    store_product_id: str,
    update_data: UpdateSchema
) -> Optional[dict]:  # ← Return dict, not ORM object
    """
    Example: Update operation with relationship loading
    """
    # 1. Fetch object within session
    result = await self.db.execute(
        select(Model).where(Model.id == store_product_id)
    )
    obj = result.scalar_one_or_none()
    if not obj:
        return None
    
    # 2. Apply updates and flush
    obj.field = update_data.field
    await self.db.flush()
    
    # 3. Load relationships BEFORE commit (critical!)
    related = await self.db.execute(
        select(RelatedModel).where(RelatedModel.id == obj.related_id)
    )
    related_obj = related.scalar_one_or_none()
    
    # 4. Commit changes
    await self.db.commit()
    
    # 5. Re-fetch for database-updated fields (like updated_at)
    fresh = await self.db.execute(
        select(Model).where(Model.id == store_product_id)
    )
    fresh_obj = fresh.scalar_one_or_none()
    
    # 6. Serialize to dict while session still active
    return self._serialize_model(fresh_obj, related_obj)
```

### Serialization Helper Method

```python
def _serialize_with_relationships(self, obj, related_obj, nested_obj):
    """
    Build a dict from ORM objects while session is active.
    Takes explicit parameters - NEVER accesses ORM relationships.
    """
    return {
        'id': str(obj.id),
        'name': obj.name,
        'created_at': obj.created_at.isoformat() if obj.created_at else None,
        'updated_at': obj.updated_at.isoformat() if obj.updated_at else None,
        'related': {
            'id': str(related_obj.id),
            'name': related_obj.name,
            'nested': {
                'id': str(nested_obj.id),
                'name': nested_obj.name,
            } if nested_obj else None
        } if related_obj else None
    }
```

### Endpoint Handler

```python
@router.put("/{item_id}")
async def update_item(
    item_id: str,
    item_data: ItemUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update endpoint - service returns dict"""
    service = ItemService(db)
    
    # Service returns dict, not ORM object
    result = await service.update_item(item_id, item_data)
    
    if not result:
        raise HTTPException(status_code=404, detail="Not found")
    
    # Return dict directly - no Pydantic validation needed
    return result
```

## When to Use This Pattern

✅ **Use dict serialization for:**
- Any operation that modifies state (CREATE, UPDATE, DELETE)
- Operations that access multiple related objects
- Operations that need fresh timestamps from the database
- Complex nested relationships that need manual loading

❌ **Can skip for:**
- Simple reads with minimal post-commit access
- Operations that don't access relationships
- Operations that don't need fresh database values

## Critical Gotchas

### 1. Access DB-Updated Fields After Re-Fetch
```python
# ❌ WRONG - Will cause greenlet error
obj.updated_at  # This triggers lazy-load after commit()

# ✅ RIGHT - Re-fetch first, then serialize
fresh_obj = await db.execute(select(Model)...)
fresh_obj.updated_at  # Safe, just loaded from DB
```

### 2. Load Relationships Before Commit
```python
# ❌ WRONG - Relationships expire after commit
await db.flush()
await db.commit()  # Now obj.related is expired
related = obj.related  # Triggers lazy-load attempt

# ✅ RIGHT - Load before commit
await db.flush()
related = await db.execute(select(Related)...)  # Load explicitly
await db.commit()  # Safe, already in memory
```

### 3. Never Return ORM Objects from Service
```python
# ❌ WRONG - Endpoint receives expired objects
async def update():
    obj.field = new_value
    await db.commit()
    return obj  # Expired, relationships null

# ✅ RIGHT - Return dict
async def update():
    obj.field = new_value
    await db.commit()
    fresh = await db.execute(select(...))
    return self._serialize(fresh, related)
```

## Real-World Example: Store Product Update

```python
# services/store_product_service.py

async def update_store_product(
    self,
    store_product_id: str,
    update_data: StoreProductUpdate
) -> Optional[dict]:
    """Update stock quantity, price, or availability"""
    
    # Fetch the store product
    result = await self.db.execute(
        select(StoreProduct).where(StoreProduct.id == store_product_id)
    )
    store_product = result.scalar_one_or_none()
    if not store_product:
        return None
    
    # Apply updates
    if update_data.stock_quantity is not None:
        store_product.stock_quantity = update_data.stock_quantity
    if update_data.store_price is not None:
        store_product.store_price = update_data.store_price
    if update_data.is_available is not None:
        store_product.is_available = update_data.is_available
    
    await self.db.flush()
    
    # Load product and category BEFORE commit
    product_result = await self.db.execute(
        select(Product).options(selectinload(Product.category))
        .where(Product.id == store_product.product_id)
    )
    product = product_result.scalar_one_or_none()
    category = product.category if product else None
    
    # Commit the changes
    await self.db.commit()
    
    # Re-fetch for updated timestamps
    fresh_result = await self.db.execute(
        select(StoreProduct).where(StoreProduct.id == store_product_id)
    )
    fresh_store_product = fresh_result.scalar_one_or_none()
    
    # Serialize to dict
    return self._serialize_store_product_with_product(
        fresh_store_product,
        product,
        category
    )

def _serialize_store_product_with_product(self, sp, product, category):
    """Build dict while session active"""
    return {
        'id': str(sp.id),
        'store_id': str(sp.store_id),
        'product_id': str(sp.product_id),
        'stock_quantity': sp.stock_quantity,
        'store_price': float(sp.store_price),
        'is_available': sp.is_available,
        'created_at': sp.created_at.isoformat() if sp.created_at else None,
        'updated_at': sp.updated_at.isoformat() if sp.updated_at else None,
        'product': {
            'id': str(product.id),
            'name': product.name,
            'description': product.description,
            'category_id': str(product.category_id),
            'category': {
                'id': str(category.id),
                'name': category.name,
            } if category else None
        } if product else None
    }
```

## Testing the Pattern

```python
# Test that dict serialization works
async def test_update_returns_dict():
    service = StoreProductService(db)
    result = await service.update_store_product(sp_id, update_data)
    
    # Should be dict, not ORM object
    assert isinstance(result, dict)
    assert result['stock_quantity'] == 150
    assert result['product'] is not None
    assert result['product']['category'] is not None
```

## Performance Considerations

1. **Extra Query**: Re-fetching after commit adds one extra query, but eliminates greenlet errors and ensures fresh timestamps
2. **Eager Loading**: Use `selectinload()` to avoid N+1 queries when loading relationships
3. **Dict Building**: Converting to dict is negligible overhead vs. database operations

## Migration Path for Existing Code

For existing endpoints that return ORM objects:

1. Add serialization helper method to service
2. Change service return type from `Model` to `dict`
3. Implement dict-building logic
4. Update endpoint to return dict directly (no `response_model`)
5. Test endpoint to verify relationships are populated

## Summary

**The pattern is simple: Serialize to dicts BEFORE the session closes.**

This eliminates:
- Greenlet errors from lazy-loading
- Null relationships in responses
- Race conditions with timestamp updates
- Complex Pydantic validation logic

Return plain dicts from services, let FastAPI serialize them to JSON. Clean, predictable, and eliminates async/ORM gotchas.
