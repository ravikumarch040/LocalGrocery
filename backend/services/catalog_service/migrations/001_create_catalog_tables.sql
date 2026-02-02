-- Catalog Service Database Migration
-- Creates: categories, products, store_products tables with indexes and FTS support

-- ==================== Categories Table ====================
CREATE TABLE IF NOT EXISTS categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    parent_id UUID REFERENCES categories(id) ON DELETE SET NULL,
    icon_url VARCHAR(500),
    display_order INTEGER DEFAULT 0 CHECK (display_order >= 0),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for categories
CREATE INDEX IF NOT EXISTS idx_categories_parent_id ON categories(parent_id);
CREATE INDEX IF NOT EXISTS idx_categories_slug ON categories(slug);
CREATE INDEX IF NOT EXISTS idx_categories_is_active ON categories(is_active);
CREATE INDEX IF NOT EXISTS idx_categories_display_order ON categories(display_order);

-- ==================== Products Table ====================
CREATE TABLE IF NOT EXISTS products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(200) NOT NULL,
    description TEXT,
    category_id UUID NOT NULL REFERENCES categories(id) ON DELETE RESTRICT,
    base_price DECIMAL(10, 2) NOT NULL CHECK (base_price >= 0),
    unit VARCHAR(20) NOT NULL DEFAULT 'piece',
    image_url VARCHAR(500),
    variants JSONB DEFAULT '[]'::jsonb,
    search_vector TSVECTOR,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT check_variants_array CHECK (jsonb_typeof(variants) = 'array')
);

-- Indexes for products
CREATE INDEX IF NOT EXISTS idx_products_category_id ON products(category_id);
CREATE INDEX IF NOT EXISTS idx_products_is_active ON products(is_active);
CREATE INDEX IF NOT EXISTS idx_products_base_price ON products(base_price);
CREATE INDEX IF NOT EXISTS idx_products_variants ON products USING GIN (variants);

-- Full-Text Search index (critical for search performance)
CREATE INDEX IF NOT EXISTS idx_products_search_vector ON products USING GIN (search_vector);

-- ==================== Store Products Table ====================
CREATE TABLE IF NOT EXISTS store_products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    store_id UUID NOT NULL,
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    stock_quantity INTEGER DEFAULT 0 CHECK (stock_quantity >= 0),
    store_price DECIMAL(10, 2) CHECK (store_price IS NULL OR store_price >= 0),
    is_available BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT unique_store_product UNIQUE (store_id, product_id)
);

-- Indexes for store_products
CREATE INDEX IF NOT EXISTS idx_store_products_store_id ON store_products(store_id);
CREATE INDEX IF NOT EXISTS idx_store_products_product_id ON store_products(product_id);
CREATE INDEX IF NOT EXISTS idx_store_products_is_available ON store_products(is_available);
CREATE INDEX IF NOT EXISTS idx_store_products_composite ON store_products(store_id, is_available);

-- ==================== Triggers ====================

-- Update updated_at timestamp automatically
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_categories_updated_at
    BEFORE UPDATE ON categories
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_products_updated_at
    BEFORE UPDATE ON products
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_store_products_updated_at
    BEFORE UPDATE ON store_products
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Auto-update search_vector on product insert/update
CREATE OR REPLACE FUNCTION update_product_search_vector()
RETURNS TRIGGER AS $$
BEGIN
    NEW.search_vector := 
        setweight(to_tsvector('english', COALESCE(NEW.name, '')), 'A') ||
        setweight(to_tsvector('english', COALESCE(NEW.description, '')), 'B');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_product_search_vector
    BEFORE INSERT OR UPDATE OF name, description ON products
    FOR EACH ROW
    EXECUTE FUNCTION update_product_search_vector();

-- ==================== Sample Data (Optional - for development) ====================

-- Sample categories
INSERT INTO categories (name, slug, description, display_order) VALUES
    ('Fruits & Vegetables', 'fruits-vegetables', 'Fresh fruits and vegetables', 1),
    ('Dairy & Eggs', 'dairy-eggs', 'Milk, cheese, yogurt, and eggs', 2),
    ('Rice & Atta', 'rice-atta', 'Rice, wheat flour, and grains', 3),
    ('Snacks & Beverages', 'snacks-beverages', 'Chips, cookies, soft drinks', 4)
ON CONFLICT (slug) DO NOTHING;

-- Sample products
WITH category_ids AS (
    SELECT id, slug FROM categories WHERE slug IN ('fruits-vegetables', 'dairy-eggs', 'rice-atta')
)
INSERT INTO products (name, description, category_id, base_price, unit, variants)
SELECT 
    'Basmati Rice',
    'Premium quality basmati rice',
    (SELECT id FROM category_ids WHERE slug = 'rice-atta'),
    120.00,
    'kg',
    '[
        {"name": "1kg", "price": 120.00, "sku": "RICE-1KG"},
        {"name": "5kg", "price": 580.00, "sku": "RICE-5KG"},
        {"name": "10kg", "price": 1100.00, "sku": "RICE-10KG"}
    ]'::jsonb
WHERE NOT EXISTS (SELECT 1 FROM products WHERE name = 'Basmati Rice');

COMMENT ON TABLE categories IS 'Product categories with hierarchical support';
COMMENT ON TABLE products IS 'Product catalog with JSONB variants and Full-Text Search';
COMMENT ON TABLE store_products IS 'Store-specific product inventory and pricing';
COMMENT ON COLUMN products.search_vector IS 'Automatically updated TSVECTOR for FTS';
COMMENT ON COLUMN products.variants IS 'JSONB array of product variants (size, price, SKU)';
