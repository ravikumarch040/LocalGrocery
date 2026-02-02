# Category Seeding Guide

This guide explains how to seed the Catalog Service database with categories and subcategories.

## Automatic Seeding (Recommended)

Categories are **automatically seeded** when the Catalog Service starts up. No manual action required.

**Process:**
1. Service starts → Creates database tables
2. Runs seeding function → Inserts 15 categories with 77 total subcategories
3. Idempotent → Won't duplicate if run multiple times

## Manual Seeding (Optional)

If you need to reseed the database manually:

### From within the catalog_service directory:

```bash
# Activate venv
.\venv\Scripts\Activate.ps1

# Run seeding script
python -m app.seeds.cli
```

### Or from workspace root:

```powershell
cd backend\services\catalog_service
.\venv\Scripts\Activate.ps1
python -m app.seeds.cli
```

## Categories Seeded

The seeding script populates **15 main categories** with **77 subcategories**:

1. **Fruits & Vegetables** (5 subcategories)
2. **Grains, Cereals & Pulses** (5 subcategories)
3. **Dairy, Milk & Eggs** (6 subcategories)
4. **Meat, Fish & Seafood** (4 subcategories)
5. **Bakery & Bread** (5 subcategories)
6. **Oils, Spices & Condiments** (5 subcategories)
7. **Beverages** (5 subcategories)
8. **Snacks & Dry Foods** (6 subcategories)
9. **Frozen Foods** (4 subcategories)
10. **Baby Food & Nutrition** (5 subcategories)
11. **Health & Wellness** (4 subcategories)
12. **Beauty & Personal Care** (6 subcategories)
13. **Household & Cleaning** (5 subcategories)
14. **Pet Supplies** (3 subcategories)
15. **Ready-to-Cook & Meal Kits** (3 subcategories)

## Testing

After seeding, you can:

1. **List categories:**
   ```bash
   GET http://localhost:8002/api/v1/categories
   ```

2. **List subcategories for a category:**
   ```bash
   GET http://localhost:8002/api/v1/categories/{category_id}/subcategories
   ```

3. **Create a product with a seeded category:**
   ```bash
   POST http://localhost:8002/api/v1/products
   {
     "name": "Basmati Rice",
     "description": "Premium quality basmati rice",
     "category_id": "{category_id_from_seeded_data}",
     "base_price": 350.00,
     "unit": "kg",
     "image_url": "https://example.com/rice.jpg"
   }
   ```

## Troubleshooting

**Issue:** Categories not seeded on startup
- **Solution:** Check Catalog Service logs for errors. Run manual seeding with `python -m app.seeds.cli`

**Issue:** Duplicate entries after reseeding
- **Solution:** Seeding is idempotent by design. If you see duplicates, check the database directly.

**Issue:** Foreign key constraint errors when creating products
- **Solution:** Ensure categories are seeded first. Use a valid `category_id` from seeded data.

## Database Schema

**Categories table:**
```sql
CREATE TABLE categories (
  id UUID PRIMARY KEY,
  name VARCHAR(255) UNIQUE NOT NULL,
  description TEXT,
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

**Subcategories table:**
```sql
CREATE TABLE subcategories (
  id UUID PRIMARY KEY,
  category_id UUID NOT NULL REFERENCES categories(id),
  name VARCHAR(255) NOT NULL,
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(category_id, name)
);
```
