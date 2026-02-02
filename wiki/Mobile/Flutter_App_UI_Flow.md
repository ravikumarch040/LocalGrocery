# Flutter App UI Flows

(Mobile-first, low learning curve)

## 👥 CUSTOMER APP FLOW
Splash
 → Phone Login (OTP)
 → Location Permission
 → Home
     → Categories
     → Search
     → Store Listing
         → Product List
             → Product Detail
                 → Add to Cart
 → Cart
 → Checkout
     → Address
     → Payment
 → Order Tracking
 → Order History
 → Wallet & Loyalty
 → Profile

## 🏪 RETAILER APP FLOW
Splash
 → Login
 → Store Status (Open/Close)
 → Orders
     → Order Detail
         → Accept / Reject
         → Pack
 → Inventory
     → Add Product
     → Update Stock
 → Offers
 → Earnings
 → Settlements
 → Profile & KYC

## 🚚 DELIVERY APP FLOW
Login
 → Available Orders
 → Accept Delivery
 → Pickup Navigation
 → Drop Navigation
 → Mark Delivered
 → Earnings

## 🧭 NAVIGATION (Flutter)

**Bottom Navigation for Customers:**
Home | Orders | Wallet | Profile

**Retailer:**
Orders | Inventory | Earnings | Profile

**State Management:** Riverpod / Bloc

Offline inventory cache for retailers
