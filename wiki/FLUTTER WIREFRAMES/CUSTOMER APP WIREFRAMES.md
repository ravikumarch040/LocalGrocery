# CUSTOMER APP WIREFRAMES

## 1. Splash Screen

**Purpose:** Branding + silent auth check

**UI**
- Center: App Logo
- Bottom: “Powered by Local Stores”
- Loader (while checking token)

**Logic**
- If logged in → Home
- Else → Login

## 2. Login / OTP Screen

**UI**
- Title: Enter your mobile number
- Phone input (+91 auto)
- Primary CTA: Send OTP
- Secondary: Privacy policy link

**OTP Screen**
- 6-digit OTP input
- Auto-read OTP
- CTA: Verify
- Resend timer (30 sec)

## 3. Location Permission Screen

**UI**
- Illustration (map/store)
- Text: Find nearby stores
- CTA: Allow Location
- Secondary: Enter location manually

## 4. Home Screen (Bottom Nav Root)

**Bottom Navigation**
- Home | Orders | Wallet | Profile

**Home – Default View**
- **Top bar:**
  - Location selector
  - Cart icon (badge)
  - Search bar (with mic icon 🎤)
- Category chips (horizontal)
- Nearby stores carousel
- Recommended products grid
- Banner (offers / subscription)

**Widgets**
- SliverAppBar
- GridView
- CachedNetworkImage

## 5. Search Screen

**UI**
- Search input (auto focus)
- Voice search button
- Recent searches
- Filter icon

**Filters**
- Price range
- Brand
- Store distance
- Availability
- Delivery time

## 6. Store Listing Screen

**UI**
- Store cards:
  - Store name
  - Rating ⭐
  - Distance
  - ETA
  - Open/Closed badge
- Tap → Store Detail

## 7. Store Detail / Product List

**UI**
- **Store header:**
  - Name
  - Delivery fee
  - Minimum order
- Category tabs
- **Product cards:**
  - Image
  - Name
  - Price
  - [+ Add] button
- **Sticky Bottom**
  - View Cart CTA (when items added)

## 8. Product Detail Screen

**UI**
- Product image carousel
- Name, brand
- Variant selector (1kg / 5kg)
- Price & discount
- Quantity stepper
- CTA: Add to Cart

## 9. Cart Screen

**UI**
- Store-wise grouping
- Item list with qty controls
- Coupon apply
- **Bill breakup:**
  - Item total
  - Delivery
  - Discount
  - Grand total

**CTA**
- Proceed to Checkout

## 10. Checkout Screen

**Steps**
- Delivery Address
- Delivery Slot
- Payment Method

**Payment Options**
- UPI
- Card
- Wallet
- BNPL
- COD (if enabled)

**CTA**
- Place Order

## 11. Order Tracking Screen

**UI**
- Order status timeline
- Store name
- Rider info (name + call)
- Live map
- ETA

**CTA**
- Help / Chat

## 12. Orders History

**UI**
- List of past orders
- Status badge
- Reorder button

## 13. Wallet & Loyalty

**UI**
- Wallet balance
- Loyalty points
- Earned / Redeemed history
- Redeem CTA

## 14. Profile Screen

**UI**
- User details
- Saved addresses
- Language selector
- Notifications toggle
- Logout
