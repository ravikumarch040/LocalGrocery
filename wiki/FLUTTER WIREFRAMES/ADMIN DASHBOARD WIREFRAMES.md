# 🖥 ADMIN DASHBOARD – LOW-FIDELITY WIREFRAMES

Audience: Ops, Finance, Support, Growth, Founders
Goal: Control, visibility, fast action

## 0️⃣ Admin Dashboard Layout (Base)
```
Global Layout
---------------------------------------------------------
| LOGO | Search 🔍 | Notifications 🔔 | Admin Profile |
---------------------------------------------------------
| Sidebar        | Main Content Area                    |
|----------------|--------------------------------------|
| Dashboard      |                                      |
| Retailers      |                                      |
| Customers      |                                      |
| Orders         |                                      |
| Payments       |                                      |
| Settlements    |                                      |
| Delivery       |                                      |
| Catalog        |                                      |
| Promotions     |                                      |
| Analytics      |                                      |
| Support        |                                      |
| Settings       |                                      |
---------------------------------------------------------
```

## 1️⃣ ADMIN – DASHBOARD (A-01)
**Purpose**

High-level business snapshot

```
---------------------------------------------------------
| DASHBOARD                                             |
---------------------------------------------------------
| Orders Today | Revenue Today | Active Stores | Users |
|   1,250      |  ₹4,80,000    |     420       | 8,200 |
---------------------------------------------------------
| Orders Trend (Graph Placeholder)                       |
|                                                       |
---------------------------------------------------------
| Top Stores        | Top Products                       |
| Store A ₹45k     | Rice 25kg                           |
| Store B ₹38k     | Milk 1L                             |
---------------------------------------------------------
| Alerts                                                |
| ⚠ High order failure in City X                        |
---------------------------------------------------------
```

## 2️⃣ ADMIN – RETAILER MANAGEMENT (A-02)
**Purpose**

Approve, manage, monitor retailers

```
---------------------------------------------------------
| RETAILERS                                             |
---------------------------------------------------------
| 🔍 Search | Status ▼ | City ▼ | KYC ▼                |
---------------------------------------------------------
| Store Name | Owner | City | KYC | Status | Action  |
|-------------------------------------------------------|
| ABC Store  | Ravi  | HYD  | PENDING | OFF | [View] |
| XYZ Mart   | Suresh| BLR  | OK      | ON  | [View] |
---------------------------------------------------------
```

🔎 Retailer Detail (A-02-D)
```
---------------------------------------------------------
| Store: ABC Store                                     |
---------------------------------------------------------
| Owner Name: Ravi Kumar                               |
| Phone: +91xxxx                                       |
| City: Hyderabad                                      |
| Commission: 5%                                      |
---------------------------------------------------------
| Documents                                            |
| PAN: [View]  GST: [View]  Bank: [View]               |
---------------------------------------------------------
| [ Approve ]   [ Reject ]   [ Suspend ]               |
---------------------------------------------------------
```

## 3️⃣ ADMIN – CUSTOMER MANAGEMENT (A-03)
**Purpose**

Support, fraud prevention, engagement

```
---------------------------------------------------------
| CUSTOMERS                                             |
---------------------------------------------------------
| 🔍 Search | Phone | Status ▼                          |
---------------------------------------------------------
| Name | Phone | Orders | Wallet | Status | Action     |
|-------------------------------------------------------|
| Anil | +91xx | 24     | ₹350   | Active | [View]    |
---------------------------------------------------------
```

👤 Customer Detail (A-03-D)
```
---------------------------------------------------------
| Customer: Anil                                       |
---------------------------------------------------------
| Orders: 24                                           |
| Wallet Balance: ₹350                                 |
| BNPL Active: Yes                                     |
---------------------------------------------------------
| Actions                                              |
| [ Block ] [ Refund ] [ Adjust Wallet ]               |
---------------------------------------------------------
```

## 4️⃣ ADMIN – ORDER MANAGEMENT (A-04)
**Purpose**

Ops visibility, issue resolution

```
---------------------------------------------------------
| ORDERS                                                |
---------------------------------------------------------
| 🔍 Order ID | Status ▼ | City ▼ | Date ▼             |
---------------------------------------------------------
| Order ID | Store | Amount | Status | Action         |
|-------------------------------------------------------|
| #12345   | ABC   | ₹560   | DELAYED | [View]        |
---------------------------------------------------------
```

📦 Order Detail (A-04-D)
```
---------------------------------------------------------
| Order #12345                                         |
---------------------------------------------------------
| Customer: Anil                                       |
| Store: ABC Store                                     |
| Payment: UPI (Paid)                                  |
---------------------------------------------------------
| Order Timeline                                       |
| ✔ Placed → ✔ Packed → ⏳ Out for delivery            |
---------------------------------------------------------
| Actions                                              |
| [ Reassign Rider ] [ Refund ] [ Cancel ]             |
---------------------------------------------------------
```

## 5️⃣ ADMIN – PAYMENTS & SETTLEMENTS (A-05)
**Purpose**

Finance & compliance

```
---------------------------------------------------------
| PAYMENTS                                              |
---------------------------------------------------------
| 🔍 Date ▼ | Gateway ▼ | Status ▼                     |
---------------------------------------------------------
| Order | Amount | Method | Status | Action           |
|-------------------------------------------------------|
| #12345 | ₹560  | UPI    | SUCCESS | [View]          |
---------------------------------------------------------
```

💰 Settlements (A-05-S)
```
---------------------------------------------------------
| SETTLEMENTS                                           |
---------------------------------------------------------
| Retailer | Amount | Status | Payout Date | Action   |
|-------------------------------------------------------|
| ABC Store| ₹12,500| PENDING| 15-May      | [Pay]   |
---------------------------------------------------------
```

## 6️⃣ ADMIN – DELIVERY OPS (A-06)
**Purpose**

Delivery performance monitoring

```
---------------------------------------------------------
| DELIVERY                                              |
---------------------------------------------------------
| Active Riders: 120                                    |
| Orders In Transit: 340                                |
---------------------------------------------------------
| Rider | Orders | Avg ETA | Status                    |
|-------------------------------------------------------|
| Ravi  | 6      | 22 min  | Active                    |
---------------------------------------------------------
```

## 7️⃣ ADMIN – CATALOG & PRICING (A-07)
**Purpose**

Control product quality & pricing abuse

```
---------------------------------------------------------
| CATALOG                                               |
---------------------------------------------------------
| 🔍 Product | Category ▼ | Status ▼                  |
---------------------------------------------------------
| Product | Brand | Avg Price | Active | Action       |
|-------------------------------------------------------|
| Rice 5kg | IndiaGate | ₹450 | Yes | [Edit]        |
---------------------------------------------------------
```

## 8️⃣ ADMIN – PROMOTIONS & OFFERS (A-08)
**Purpose**

Growth & retention

```
---------------------------------------------------------
| PROMOTIONS                                            |
---------------------------------------------------------
| [ Create New Offer ]                                  |
---------------------------------------------------------
| Code | Discount | Validity | Status | Action        |
|-------------------------------------------------------|
| SAVE50 | ₹50    | 30-May   | Active | [Edit]       |
---------------------------------------------------------
```

## 9️⃣ ADMIN – ANALYTICS (A-09)
**Purpose**

Data-driven decisions

```
---------------------------------------------------------
| ANALYTICS                                             |
---------------------------------------------------------
| Orders by City (Graph)                                |
| Revenue Trend (Graph)                                 |
---------------------------------------------------------
| KPI Summary                                          |
| Conversion Rate: 38%                                 |
| Repeat Users: 62%                                    |
---------------------------------------------------------
```

## 🔟 ADMIN – SUPPORT & DISPUTES (A-10)
**Purpose**

Customer satisfaction & ops trust

```
---------------------------------------------------------
| SUPPORT                                               |
---------------------------------------------------------
| Ticket | User | Issue | Status | Action             |
|-------------------------------------------------------|
| #455   | Anil | Late delivery | Open | [Resolve]  |
---------------------------------------------------------
```

## 1️⃣1️⃣ ADMIN – SETTINGS (A-11)
**Purpose**

Platform configuration

```
---------------------------------------------------------
| SETTINGS                                              |
---------------------------------------------------------
| Commission Rules                                     |
| Delivery Fees                                        |
| BNPL Limits                                          |
| Notification Templates                               |
| Role Management                                      |
---------------------------------------------------------
```
