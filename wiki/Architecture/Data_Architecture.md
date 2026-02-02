# Data Architecture

## PostgreSQL
Used for transactional data:
- Users
- Orders
- Payments
- Settlements
- Wallets

## MongoDB
Used for flexible catalog data:
- Products
- Variants
- Attributes

## Caching
Redis used for:
- Cart
- Inventory
- Session data
