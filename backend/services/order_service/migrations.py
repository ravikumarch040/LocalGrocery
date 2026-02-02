"""Alembic migrations for Order Service (manual migration)"""

migration_sql = """
-- Create order status and payment status enums
CREATE TYPE order_status AS ENUM (
    'PLACED',
    'CONFIRMED',
    'PACKED',
    'OUT_FOR_DELIVERY',
    'DELIVERED',
    'CANCELLED'
);

CREATE TYPE payment_status AS ENUM (
    'PENDING',
    'PAID',
    'FAILED',
    'REFUNDED'
);

-- Create orders table
CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID NOT NULL,
    store_id UUID NOT NULL,
    order_number VARCHAR(50) NOT NULL UNIQUE,
    status order_status NOT NULL DEFAULT 'PLACED',
    payment_status payment_status NOT NULL DEFAULT 'PENDING',
    
    subtotal NUMERIC(10, 2) NOT NULL,
    tax NUMERIC(10, 2) DEFAULT 0,
    delivery_fee NUMERIC(10, 2) DEFAULT 0,
    discount NUMERIC(10, 2) DEFAULT 0,
    total_amount NUMERIC(10, 2) NOT NULL,
    
    delivery_address JSONB,
    payment_method VARCHAR(50),
    payment_gateway VARCHAR(50),
    payment_gateway_order_id VARCHAR(255),
    idempotency_key VARCHAR(255) UNIQUE,
    notes TEXT,
    metadata JSONB DEFAULT '{}',
    
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    confirmed_at TIMESTAMP WITH TIME ZONE,
    delivered_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX ix_orders_customer_id ON orders(customer_id);
CREATE INDEX ix_orders_store_id ON orders(store_id);
CREATE INDEX ix_orders_order_number ON orders(order_number);
CREATE INDEX ix_orders_status ON orders(status);
CREATE INDEX ix_orders_payment_status ON orders(payment_status);
CREATE INDEX ix_orders_idempotency_key ON orders(idempotency_key);
CREATE INDEX ix_orders_customer_created ON orders(customer_id, created_at);
CREATE INDEX ix_orders_store_status ON orders(store_id, status);

-- Create order_items table
CREATE TABLE order_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id UUID NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    product_id UUID NOT NULL,
    
    product_name VARCHAR(255) NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price NUMERIC(10, 2) NOT NULL,
    total_price NUMERIC(10, 2) NOT NULL,
    
    variant_data JSONB DEFAULT '{}',
    status order_status NOT NULL DEFAULT 'PLACED',
    
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX ix_order_items_order_id ON order_items(order_id);
CREATE INDEX ix_order_items_product_id ON order_items(product_id);
"""
