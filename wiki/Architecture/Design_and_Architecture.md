# Design and Architecture

## 1 — High Level Architecture (Modules & Data Flow)

**Mobile App (Flutter recommended)**: Single codebase for Android/iOS, fast UI, great on low-end devices.

**API Gateway (edge)**: Authentication, rate-limiting, request routing, WAF.

**Backend microservices (stateless, containerized)**: Auth, User/Profile, Catalog, Inventory, Pricing & Offers, Cart, Order, Payment, Delivery & Driver, Notifications, Analytics, Accounting/Settlement, Admin.

**Event streaming / message bus**: For async workflows, order lifecycle, notifications, search indexing, inventory events.

**Datastores**: 
- OLTP RDBMS for transactions (Postgres)
- Document store for flexible product metadata (optional MongoDB)
- Search engine for catalog search (Elasticsearch/OpenSearch)
- Redis for caching and sessions

**Real-time subsystem**: WebSockets or socket gateway (for rider/customer live tracking/ETA updates).

**Integrations**: 
- Payment gateways (Razorpay / Cashfree)
- UPI / wallets
- BNPL providers (LazyPay / Simpl / others)
- Maps & routing (Google Maps or Mapbox + GraphHopper for route optimization)
- SMS/OTP (MSG91 / Twilio)
- Push (Firebase Cloud Messaging)

**Data warehouse & analytics**: Event lake (S3), ETL pipelines → analytics store (BigQuery / Redshift / ClickHouse) for ML & business intelligence.

**CI/CD + infra**: GitHub Actions / GitLab CI, container registry (ECR/GCR), Kubernetes (managed EKS/GKE/AKS), IaC (Terraform), observability (Prometheus + Grafana + ELK/Opensearch).

**Data flow example**: Customer places order → API Gateway → Order service → persist to Postgres → emit order-created event to Kafka → Inventory service reserves stock, Payment service charges via Razorpay/Cashfree → on success emit paid event → Delivery service schedules (route optimizer) → driver picks & updates → order delivered → settlement flows to retailer ledger and payouts.

## 2 — Recommended Concrete Tech Stack (Opinionated)

### Mobile

**Framework**: Flutter (Dart) — single codebase, excellent performance, smooth native UI. (Recommended for mobile-only product with rich UI & offline caching.)

**State management**: Riverpod / Bloc

**Local DB / caching on device**: SQLite (moor/drift) or Hive for small caches

**Realtime**: socket.io or WebSocket + notifications via FCM.

### API / Backend

**Language / framework**: Node.js + TypeScript (NestJS) or Golang for critical high-throughput services. (NestJS gives rapid developer productivity + modular microservices; Golang for very high throughput microservices like Routing/Realtime.)

**API Gateway**: Kong (open-source) or AWS API Gateway / Apigee for managed.

**Auth**: JWT + OAuth2; use AWS Cognito or Auth0 (or a homegrown Identity microservice for full control).

### Databases & Caching

**Primary transactional DB**: PostgreSQL (managed RDS / Aurora) — ACID, strong relational guarantees (orders, payments, settlements). Evidence: Postgres performs reliably at scale for transactional workloads.

**Product metadata (optional)**: MongoDB if you need highly flexible schemas for variant-rich catalogs; otherwise, model variants in Postgres. (Tradeoffs covered below.)

**Search engine**: Elasticsearch (hosted or managed) or OpenSearch if you want fully open stack. Elasticsearch tends to have performance advantages in some benchmarks; OpenSearch is a viable open alternative. Choose based on licensing, hosting preferences and feature set.

**Cache & fast queues**: Redis (ElastiCache / managed) for product caches, sessions, rate limits, distributed locks.

**Message broker / event streaming**: Apache Kafka for high-throughput event streaming (analytics, inventory events, rider telemetry). Use RabbitMQ for transactional queues where complex routing & ack semantics matter. Many systems use both (Kafka for streams, RabbitMQ for transactional work).

### Realtime & Location

**Push notifications**: Firebase Cloud Messaging (FCM) for Android/iOS push. (Free and cross-platform.)

**Maps & routing**: Mapbox for customizable maps & navigation (cost-effective) or Google Maps Platform for coverage and rich Places data — pick one based on pricing and features; both provide Directions/Distance Matrix. Use GraphHopper (or Mapbox Optimization) for route optimization / vehicle routing problems.

### Payments & Financials (India)

**Primary payment gateways**: Razorpay or Cashfree — both have rich SDKs for mobile and server, UPI, wallets, cards, payouts & vendor settlements; support instant settlements/payouts features. Razorpay and Cashfree are widely used in India. (Integrate 2 gateways as fallback.)

**BNPL / Credit**: Integrate with LazyPay / Simpl / ZestMoney (or local BNPL partners) depending on merchant agreements. Consider wallet + internal credit (micro-credit) for trusted customers.

**Payouts to retailers**: Use Cashfree Payouts or RazorpayX (or partner bank APIs) for automated settlements and reconciliation.

### Infrastructure & DevOps

**Cloud**: AWS recommended for maturity & ecosystem (EKS, RDS/Aurora, ElastiCache, S3, Lambda, Kinesis). GCP or Azure are viable alternatives.

**Containers**: Docker + Kubernetes (EKS/GKE/AKS); autoscaling groups for stateless services.

**CI/CD**: GitHub Actions / GitLab CI; use image registry ECR/GCR.

**IaC**: Terraform for reproducible infra.

**Secrets & config**: AWS Secrets Manager or HashiCorp Vault.

**CDN**: CloudFront or Cloudflare for static assets & APIs edge caching.

### Observability & Security

**Logging**: Centralized ELK stack (Elasticsearch/Logstash/Kibana) or OpenSearch + Grafana.

**Metrics & tracing**: Prometheus, Grafana, and Jaeger for distributed tracing.

**Error tracking**: Sentry.

**WAF & DDoS**: Cloud provider WAF + rate limiting at API Gateway.

**PCI compliance**: Keep Payment UI & card handling via gateway hosted checkout or tokenization. Avoid storing card data.

### Analytics & ML

**Event lake**: Store events to S3 (Parquet), ETL to a warehouse: BigQuery / Redshift / ClickHouse for product analytics and personalization.

**Real-time personalization**: Kafka → feature store → online model (Redis) and offline model training in BigQuery/Databricks.

### Third-party Services (India-specific)

**SMS/OTP**: MSG91 (widely used in India) or Twilio as fallback.

**Email**: SES / SendGrid.

**KYC**: Integrate with eKYC providers if you onboard retailers (e.g., Digio, Karza).

## 3 — Architecture Diagram (Textual / Flow)

```
[Flutter App] <--HTTPS--> [API Gateway + WAF] --> {Auth, User, Catalog, Cart, Order, Payment, Delivery, Inventory, Offers, Notifications} (microservices)
                |                                \ 
                |                                 -> Kafka (events) -> Analytics DB / ML
                |                                /
                +--> Redis (cache)                -> Elasticsearch (search index)
                +--> Postgres (orders, users, settlements)
                +--> MongoDB (optional product meta)
                +--> Payment Gateways (Razorpay / Cashfree)
                +--> Maps/Routing (Mapbox/Google + GraphHopper)
                +--> Push (FCM) / SMS (MSG91)
                +--> Driver App (WebSocket/Realtime)
                +--> Admin Dashboard (role based)
```

## 4 — Why These Choices? (Short Rationales & Supporting Refs)

**Razorpay / Cashfree** — Full Indian payment features (UPI, wallets, cards, payouts) and easy mobile SDKs; recommend integrating two gateways for higher success rates and instant refunds/payouts options.

**Firebase Cloud Messaging** — Cross-platform, zero cost for push, simple SDKs for Flutter.

**Mapbox / Google + GraphHopper** — Maps + high-quality Directions/Matrix APIs; GraphHopper offers explicit route optimization for VRP (vehicle routing). Use whichever pricing/coverage fits your city footprint.

**Postgres + Kafka + Elasticsearch** — Postgres for financial/transactional integrity; Kafka for scalable event streaming for analytics & decoupled processing; Elasticsearch for fast, feature-rich search. (Elasticsearch vs OpenSearch decision depends on license/managed support choices.)

**Hybrid messaging** — Use both Kafka & RabbitMQ in hybrid mode if you need transactional queueing semantics and also stream analytics (many food delivery/e-commerce apps use this pattern).

## 5 — Non-functional Requirements & How Stack Meets Them

### Scalability
Stateless microservices + Kubernetes autoscaling. Kafka for backpressure and replayable events. Use read replicas for Postgres, partitioning, and index sharding for Elasticsearch.

### High Availability
Multi-AZ deployments for DB & Kafka; cross-region backups for DR. Use managed services where possible (RDS/Aurora, MSK, Elastic Cloud).

### Consistency & Correctness
Use Postgres for orders & settlements to guarantee ACID. Eventual-consistent updates for catalog and inventory views (use strong reservation patterns when fulfilling orders).

### Performance
Caching layer (Redis) for hot catalog & price; R/W separation for Postgres; CDN for static content; search offloaded to Elasticsearch.

### Security & Compliance
Tokenized payments via gateway, PCI scope reduction, encrypted data at rest/in transit, KYC for retailers (GST, PAN docs), role-based access control in admin.

### Cost Control
Start with managed services but design to replace components if costs blow up (e.g., move from hosted Elasticsearch to OpenSearch self-managed if needed).

## 6 — Implementation & Rollout Plan (Practical)

### Phase 0 — MVP (90 days)
- **Mobile**: Basic browse / search / cart / checkout (single store) + Razorpay integration + FCM notifications.
- **Backend**: Monolith or a small set of services (Auth, Catalog, Cart, Order, Payment) deployed on small Kubernetes cluster. Postgres RDS, Redis.
- **Minimal admin & retailer onboarding flow** (manual KYC).

### Phase 1 — Marketplace Features (months 2–4)
- Multi-vendor cart split, vendor portal (add products, inventory), settlement engine, store level stock visibility, driver app (basic).
- Add Kafka for events, Elasticsearch for search, route optimizer integration.

### Phase 2 — Scale & Differentiation (months 4–9)
- Add BNPL partners, dark stores / micro-fulfillment hooks, advanced personalization ML, driver batching & route optimization, loyalty wallet & subscriptions.

## 7 — Monitoring, SLOs & Operational Playbook

**Define SLOs**: 
- Checkout success rate > 99%
- API p95 latency < 200ms
- Order failure rate < 0.5%

**Monitoring stack**: 
- Prometheus + Grafana (latency, errors, infra)
- ELK/OpenSearch logs
- Jaeger traces
- Sentry for exceptions

**Runbook for incidents**: Payment failures, inventory oversell, delivery delays.

## 8 — Cost & Vendor Notes (India Specifics)

**Maps** can be expensive at scale; measure calls per order (distance matrix, geocoding) and consider Mapbox with local caching or Google Maps subscription plan for predictable pricing.

**Payment gateway fees**: Negotiate with Razorpay/Cashfree for volume & settlements (also consider instant settlements for retailer trust).

## 9 — Quick Checklist / Next Steps You Can Act On Immediately

- [ ] Choose mobile framework (I recommend Flutter).
- [ ] Implement a minimal checkout using Razorpay (and keep Cashfree as fallback).
- [ ] Build core services as small Node.js TypeScript services and deploy on EKS (or GKE).
- [ ] Add Postgres + Redis; keep search behind Elasticsearch indexing pipeline.
- [ ] Integrate FCM for push and MSG91 for OTPs.
- [ ] Plan Kafka for event stream ingestion early — even if initially run a small single-node cluster.

## 10 — Sources & Helpful Docs

- Razorpay docs (payments & features)
- Cashfree docs & payouts
- Firebase Cloud Messaging docs
- Mapbox pricing & Directions API; Google Maps Platform pricing & Distance Matrix
- GraphHopper Route Optimization API
- Postgres vs MongoDB comparisons and guidance
- Kafka vs RabbitMQ decision guides
- Elasticsearch vs OpenSearch comparisons
