# Detailed Component Diagram (Services, APIs, Data Stores)

```mermaid
graph TD

%% ===== CLIENTS =====
CUST[Customer Mobile App<br/>(Flutter)]
RETAILER[Retailer Mobile App<br/>(Flutter)]
DRIVER[Delivery Partner App]
ADMIN[Admin Web Dashboard]

%% ===== EDGE =====
CUST -->|HTTPS| GATEWAY
RETAILER -->|HTTPS| GATEWAY
DRIVER -->|HTTPS| GATEWAY
ADMIN -->|HTTPS| GATEWAY

GATEWAY[API Gateway<br/>Auth • Rate Limit • WAF]

%% ===== AUTH =====
GATEWAY --> AUTH[Auth Service<br/>JWT • OTP • RBAC]

%% ===== CORE SERVICES =====
GATEWAY --> USER[User & Profile Service]
GATEWAY --> STORE[Retailer / Store Service]
GATEWAY --> CATALOG[Catalog Service]
GATEWAY --> INVENTORY[Inventory Service]
GATEWAY --> SEARCH[Search Service]
GATEWAY --> CART[Cart Service]
GATEWAY --> ORDER[Order Service]
GATEWAY --> PAYMENT[Payment Service]
GATEWAY --> DELIVERY[Delivery & Routing Service]
GATEWAY --> LOYALTY[Loyalty & Wallet Service]
GATEWAY --> NOTIFY[Notification Service]
GATEWAY --> REVIEW[Ratings & Reviews Service]
GATEWAY --> ANALYTICS[Analytics Service]

%% ===== DATA STORES =====
USER --> PG[(PostgreSQL)]
STORE --> PG
ORDER --> PG
PAYMENT --> PG
LOYALTY --> PG

CATALOG --> MONGO[(MongoDB)]
INVENTORY --> PG

SEARCH --> ES[(Elasticsearch / OpenSearch)]

CART --> REDIS[(Redis Cache)]
INVENTORY --> REDIS

%% ===== EVENTS =====
ORDER --> KAFKA[(Kafka / Event Bus)]
PAYMENT --> KAFKA
DELIVERY --> KAFKA
INVENTORY --> KAFKA

KAFKA --> ANALYTICS
KAFKA --> SEARCH
KAFKA --> NOTIFY

%% ===== EXTERNAL INTEGRATIONS =====
PAYMENT --> RAZOR[Razorpay / Cashfree]
PAYMENT --> BNPL[BNPL Providers<br/>LazyPay / Simpl]

DELIVERY --> MAPS[Maps & Routing<br/>Google / Mapbox + GraphHopper]

NOTIFY --> FCM[Firebase Push]
NOTIFY --> SMS[MSG91 / Twilio]

%% ===== ADMIN =====
ADMIN --> ANALYTICS
ADMIN --> STORE
ADMIN --> SETTLEMENT[Settlement & Payout Service]

SETTLEMENT --> BANK[Payout APIs]
```
