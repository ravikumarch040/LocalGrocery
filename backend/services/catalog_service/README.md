# Catalog Service

Product catalog, category management, and search service for LocalGrocery platform.

## Features

- Product CRUD operations with JSONB variant support
- Category management (hierarchical)
- Store-product associations
- PostgreSQL Full-Text Search (FTS)
- Product image upload to S3
- Advanced filtering (category, price, availability)

## Quick Start

### Setup
```powershell
cd backend/services/catalog_service
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Run Service
```powershell
python -m uvicorn app.main:app --reload --port 8002
```

**API Docs**: http://localhost:8002/docs

### Run Tests
```powershell
pytest tests/ -v
```

## API Endpoints

### Products
- `POST /api/v1/products` - Create product
- `GET /api/v1/products/{id}` - Get product by ID
- `PUT /api/v1/products/{id}` - Update product
- `DELETE /api/v1/products/{id}` - Delete product
- `GET /api/v1/products/search` - Search products (FTS)
- `GET /api/v1/products` - List products with filters

### Categories
- `POST /api/v1/categories` - Create category
- `GET /api/v1/categories` - List all categories
- `GET /api/v1/categories/{id}` - Get category by ID
- `PUT /api/v1/categories/{id}` - Update category
- `DELETE /api/v1/categories/{id}` - Delete category

### Store Products
- `POST /api/v1/stores/{store_id}/products` - Associate product with store
- `GET /api/v1/stores/{store_id}/products` - Get store's product catalog
- `PUT /api/v1/stores/{store_id}/products/{product_id}` - Update store-specific data
- `DELETE /api/v1/stores/{store_id}/products/{product_id}` - Remove product from store

## Database Schema

### Products Table
- `id` (UUID, PK)
- `name` (VARCHAR 255)
- `description` (TEXT)
- `category_id` (UUID, FK)
- `base_price` (DECIMAL)
- `image_url` (TEXT)
- `variants` (JSONB) — sizes, flavors, etc.
- `is_active` (BOOLEAN)
- `search_vector` (TSVECTOR) — FTS index
- `created_at`, `updated_at` (TIMESTAMP)

### Categories Table
- `id` (UUID, PK)
- `name` (VARCHAR 100)
- `slug` (VARCHAR 100, unique)
- `parent_id` (UUID, FK, nullable) — hierarchical
- `icon_url` (TEXT)
- `display_order` (INTEGER)
- `created_at`, `updated_at` (TIMESTAMP)

### Store Products Table
- `id` (UUID, PK)
- `store_id` (UUID, FK)
- `product_id` (UUID, FK)
- `stock_quantity` (INTEGER)
- `store_price` (DECIMAL) — override base_price
- `is_available` (BOOLEAN)
- `created_at`, `updated_at` (TIMESTAMP)

## Product Variants (JSONB)

Example variant structure:
```json
{
  "sizes": [
    {"name": "500g", "price_modifier": 0},
    {"name": "1kg", "price_modifier": 50}
  ],
  "attributes": {
    "brand": "Fortune",
    "organic": true,
    "gluten_free": false
  }
}
```

## Full-Text Search

Products are indexed using PostgreSQL's built-in FTS:
- `search_vector` column auto-updated via trigger
- Searches `name` and `description` fields
- Ranked results by relevance

Example search query:
```sql
SELECT * FROM products
WHERE search_vector @@ to_tsquery('english', 'rice & basmati')
ORDER BY ts_rank(search_vector, to_tsquery('english', 'rice & basmati')) DESC;
```

## Configuration

**File**: `.env`

```
DATABASE_URL=postgresql+asyncpg://localgrocery:password@localhost/localgrocery
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_S3_BUCKET=localgrocery-products
AWS_REGION=us-east-1
DEBUG=True
```

## Tech Stack

- FastAPI + Uvicorn (async web framework)
- SQLAlchemy 2.0 + asyncpg (async ORM)
- PostgreSQL FTS (search)
- AWS S3 (image storage)
- Pydantic v2 (validation)
- pytest (testing)

---

**Status**: 🚧 In Development
**Port**: 8002
**Last Updated**: January 18, 2026
