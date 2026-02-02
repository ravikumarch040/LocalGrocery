# Store Product API - Quick Reference

## 🚀 API Endpoints Overview

### 1. Create Store Product
```http
POST /api/v1/store-products/
Content-Type: application/json

{
  "store_id": "uuid",
  "product_id": "uuid",
  "stock_quantity": 100,
  "store_price": 299.99,
  "is_available": true
}
```
**Response**: `201 Created`
- Full store product object with product + category nested

### 2. Get Store Product
```http
GET /api/v1/store-products/{store_product_id}
```
**Response**: `200 OK`
- Single store product with product + category

### 3. Update Store Product
```http
PUT /api/v1/store-products/{store_product_id}
Content-Type: application/json

{
  "stock_quantity": 150,
  "store_price": 289.99,
  "is_available": true
}
```
**Response**: `200 OK`
- Updated store product with fresh timestamps

### 4. List Store Products
```http
GET /api/v1/store-products/store/{store_id}?is_available=true&category_id=uuid&page=1&page_size=20
```
**Response**: `200 OK` (array)
- List of store products for a specific store
- Each item includes product + category

### 5. Delete Store Product (Soft Delete)
```http
DELETE /api/v1/store-products/{store_product_id}
```
**Response**: `200 OK`
```json
{
  "success": true,
  "message": "Product removed from store successfully"
}
```

## 📊 Response Format

All responses include nested relationships:

```json
{
  "id": "uuid",
  "store_id": "uuid",
  "product_id": "uuid",
  "stock_quantity": 150,
  "store_price": 289.99,
  "is_available": true,
  "created_at": "2026-01-19T19:08:44.796765+00:00",
  "updated_at": "2026-01-19T19:08:44.874115+00:00",
  "product": {
    "id": "uuid",
    "name": "Premium Basmati Rice",
    "description": "Premium aged basmati rice from Punjab",
    "category_id": "uuid",
    "base_price": 279.99,
    "unit": "kg",
    "image_url": "https://...",
    "variants": {...},
    "is_active": true,
    "created_at": "2026-01-19T19:08:44.796765+00:00",
    "updated_at": "2026-01-19T19:08:44.874115+00:00",
    "category": {
      "id": "uuid",
      "name": "Rice",
      "slug": "rice",
      "description": "Rice and grains"
    }
  }
}
```

## ✅ Current Status

| Endpoint | Method | Status | Tested |
|----------|--------|--------|--------|
| `/api/v1/store-products/` | POST | ✅ Working | Yes |
| `/api/v1/store-products/{id}` | GET | ✅ Working | Yes |
| `/api/v1/store-products/{id}` | PUT | ✅ Working | Yes |
| `/api/v1/store-products/store/{store_id}` | GET | ✅ Working | Yes |
| `/api/v1/store-products/{id}` | DELETE | ✅ Working | Yes |

## 🔧 Common Use Cases

### Scenario 1: Add new product to store
```python
# Python/requests
response = requests.post(
    "http://localhost:8002/api/v1/store-products/",
    json={
        "store_id": "store-uuid",
        "product_id": "product-uuid",
        "stock_quantity": 50,
        "store_price": 299.99,
        "is_available": True
    }
)
# Returns 201 with full product details
```

### Scenario 2: Check product stock levels
```python
response = requests.get(
    "http://localhost:8002/api/v1/store-products/store-product-uuid"
)
stock = response.json()["stock_quantity"]
```

### Scenario 3: Update stock after sale
```python
response = requests.put(
    "http://localhost:8002/api/v1/store-products/store-product-uuid",
    json={"stock_quantity": 45}  # Was 50, sold 5
)
```

### Scenario 4: Find all available rice products in a store
```python
response = requests.get(
    "http://localhost:8002/api/v1/store-products/store/store-uuid",
    params={
        "is_available": True,
        "category_id": "rice-category-uuid"
    }
)
products = response.json()
```

## 🐛 Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| `404 Not Found` | Store product ID invalid | Check store_product_id exists |
| `409 Conflict` | Product already in store | Remove first, then re-add |
| `422 Invalid` | Missing required fields | Check all required fields present |
| `500 Internal Error` | Rare server issue | Check server logs |

## 📖 For Developers

### Understanding the Async/ORM Pattern

See `wiki/Backend/ASYNC_ORM_SERIALIZATION_PATTERN.md` for:
- Deep dive into why the pattern is needed
- How to implement it in other services
- Common gotchas and how to avoid them
- Testing strategies

### Modifying the API

If you need to:
1. **Add a field**: Update model → schema → serializer
2. **Change response format**: Update `_serialize_store_product_with_product()`
3. **Add filtering**: Update `list_store_products()` query
4. **Add validation**: Update StoreProductCreate/Update schemas

### Testing

Run the comprehensive test:
```bash
cd backend/services/catalog_service
python simple_store_product_test.py
```

Expected output:
```
[1] CREATE - ✅ 201 Created
[2] READ - ✅ 200 OK
[3] UPDATE - ✅ 200 OK
[4] LIST - ✅ 200 OK
[5] DELETE - ✅ 200 OK
```

## 🎯 Key Implementation Details

- **Service Layer**: `app/services/store_product_service.py`
- **API Endpoints**: `app/api/v1/endpoints/store_products.py`
- **Models**: `app/models.py` (StoreProduct, Product, Category)
- **Schemas**: `app/api/v1/schemas/catalog.py`

## 📌 Important Notes

1. **Delete is Soft Delete**: Products are marked as unavailable, not removed
2. **Timestamps Auto-Updated**: `created_at` and `updated_at` handled by database
3. **Relationships Always Loaded**: Product and category always included in responses
4. **All Operations Async**: Use `await` when calling service methods
5. **Pricing Logic**: `store_price` overrides `base_price` at the store level

---

For complete documentation, see:
- `STORE_PRODUCT_API_COMPLETION.md` - Detailed completion report
- `ASYNC_ORM_SERIALIZATION_PATTERN.md` - Pattern explanation
- `STORE_PRODUCT_API_SUMMARY.md` - Full summary and metrics
