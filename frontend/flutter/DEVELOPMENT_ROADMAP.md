# 🗺️ Flutter UI Implementation Roadmap

## Overview
This roadmap provides a step-by-step guide for implementing the customer, retailer, and delivery partner apps. Follow the phases in order for best results.

---

## 🎯 Phase 1: Customer App Foundation (Week 1-2)

### Sprint 1.1: Authentication & Navigation (3-4 days)

#### Step 1: Set Up Dependencies
\`\`\`yaml
# Add to apps/customer_app/pubspec.yaml
dependencies:
  # State Management
  flutter_riverpod: ^2.4.9
  
  # Navigation
  go_router: ^13.0.0
  
  # Local packages
  core:
    path: ../../packages/core
  models:
    path: ../../packages/models
  api_client:
    path: ../../packages/api_client
  
  # Storage
  shared_preferences: ^2.2.2
  flutter_secure_storage: ^9.0.0
  
  # UI
  google_fonts: ^6.1.0
\`\`\`

#### Step 2: Create Provider Infrastructure
Create these files in `apps/customer_app/lib/providers/`:
- \`auth_provider.dart\` - User authentication state
- \`cart_provider.dart\` - Shopping cart state
- \`location_provider.dart\` - User location state

#### Step 3: Set Up Navigation
Create `apps/customer_app/lib/router.dart`:
- Define all routes
- Set up route guards for authentication
- Configure deep linking

#### Step 4: Build Auth Screens
Create in `apps/customer_app/lib/screens/auth/`:
1. **splash_screen.dart**
   - Show app logo
   - Check if user is logged in
   - Navigate to login or home

2. **login_screen.dart**
   - Phone number input
   - OTP request button
   - Validation

3. **otp_screen.dart**
   - OTP input (6 digits)
   - Countdown timer
   - Resend OTP
   - Auto-verification

**Reference**: See [Customer App Wireframes](../../wiki/FLUTTER%20WIREFRAMES/CUSTOMER%20APP%20WIREFRAMES.md)

#### Success Criteria:
- [ ] User can enter phone number
- [ ] User receives OTP
- [ ] User can verify OTP and login
- [ ] Session persists across app restarts
- [ ] User can logout

---

### Sprint 1.2: Home Screen & Product Discovery (3-4 days)

#### Step 1: Create Home Screen Layout
Create `apps/customer_app/lib/screens/home/home_screen.dart`:
- App bar with location selector
- Search bar
- Category horizontal scroll
- Featured products grid
- Quick reorder section

#### Step 2: Implement Location Services
- Request location permission
- Get current location
- Reverse geocode to address
- Show location selector bottom sheet

#### Step 3: Build Category Widget
Create `apps/customer_app/lib/widgets/category_card.dart`:
- Category image
- Category name
- Product count
- Navigation to category products

#### Step 4: Build Product Card
Create `apps/customer_app/lib/widgets/product_card.dart`:
- Product image
- Product name
- Price with discount
- Add to cart button
- Quick view option

#### Step 5: Implement Search
Create `apps/customer_app/lib/screens/search/search_screen.dart`:
- Search input with debouncing
- Recent searches
- Search suggestions
- Results list

#### Success Criteria:
- [ ] Home screen displays categories
- [ ] Home screen shows featured products
- [ ] User can select location
- [ ] User can search for products
- [ ] Search results display correctly

---

### Sprint 1.3: Cart & Checkout (4-5 days)

#### Step 1: Build Cart Screen
Create `apps/customer_app/lib/screens/cart/cart_screen.dart`:
- Items grouped by store
- Quantity adjustment
- Remove item
- Coupon application
- Price breakdown
- Checkout button

#### Step 2: Implement Cart Provider
\`\`\`dart
@riverpod
class Cart extends _$Cart {
  @override
  FutureOr<CartModel?> build() async {
    // Load cart from API
  }

  Future<void> addItem(Product product, Store store) async {
    // Add item to cart
  }

  Future<void> updateQuantity(String itemId, int quantity) async {
    // Update item quantity
  }

  Future<void> removeItem(String itemId) async {
    // Remove item
  }

  Future<void> applyCoupon(String code) async {
    // Apply coupon
  }
}
\`\`\`

#### Step 3: Create Address Management
Create `apps/customer_app/lib/screens/address/`:
1. **address_list_screen.dart**
   - List saved addresses
   - Default address indicator
   - Add new address button

2. **add_address_screen.dart**
   - Address form
   - Map picker for location
   - Save as default option

#### Step 4: Build Checkout Flow
Create `apps/customer_app/lib/screens/checkout/checkout_screen.dart`:
- Address selection
- Payment method selection
- Delivery instructions
- Order summary
- Place order button

#### Step 5: Integrate Payment Gateway
Add Razorpay dependency:
\`\`\`yaml
dependencies:
  razorpay_flutter: ^1.3.6
\`\`\`

Implement payment handling:
\`\`\`dart
Future<void> initiatePayment(Order order) async {
  Razorpay razorpay = Razorpay();
  
  var options = {
    'key': AppConfig.razorpayKeyId,
    'amount': order.total * 100, // in paise
    'name': 'LocalGrocery',
    'order_id': order.id,
    // ... other options
  };

  razorpay.open(options);
}
\`\`\`

#### Success Criteria:
- [ ] User can view cart with items grouped by store
- [ ] User can adjust quantities
- [ ] User can apply coupons
- [ ] User can add/select delivery address
- [ ] User can complete payment
- [ ] Order confirmation screen shows

---

### Sprint 1.4: Order Management & Tracking (3-4 days)

#### Step 1: Orders List Screen
Create `apps/customer_app/lib/screens/orders/orders_screen.dart`:
- Tabs for Active/Past orders
- Order cards with status
- Quick reorder button
- Navigate to order details

#### Step 2: Order Details Screen
Create `apps/customer_app/lib/screens/orders/order_details_screen.dart`:
- Order status timeline
- Item list
- Price breakdown
- Delivery address
- Track order button
- Cancel order option
- Help/support

#### Step 3: Order Tracking Screen
Create `apps/customer_app/lib/screens/orders/order_tracking_screen.dart`:
- Real-time map with delivery partner location
- ETA display
- Order status updates
- Call delivery partner button
- Live updates via websocket/polling

#### Step 4: Rating & Review
Create `apps/customer_app/lib/screens/orders/rate_order_screen.dart`:
- Star rating
- Review text input
- Photo upload (optional)
- Submit button

#### Success Criteria:
- [ ] User can see order history
- [ ] User can view order details
- [ ] User can track orders in real-time
- [ ] User can cancel orders
- [ ] User can rate and review completed orders

---

### Sprint 1.5: Profile & Settings (2-3 days)

#### Step 1: Profile Screen
Create `apps/customer_app/lib/screens/profile/profile_screen.dart`:
- User info (name, phone, email)
- Edit profile option
- Saved addresses link
- Order history link
- Wallet/rewards link
- Settings link
- Logout button

#### Step 2: Settings Screen
Create `apps/customer_app/lib/screens/profile/settings_screen.dart`:
- Notifications toggle
- Language selection
- App version
- Terms & privacy links
- Help & support

#### Step 3: Wallet Screen
Create `apps/customer_app/lib/screens/profile/wallet_screen.dart`:
- Current balance
- Transaction history
- Add money option
- Cashback offers

#### Success Criteria:
- [ ] User can view and edit profile
- [ ] User can manage addresses
- [ ] User can view wallet balance
- [ ] User can change settings
- [ ] User can logout

---

## 🏪 Phase 2: Retailer App (Week 3-4)

### Sprint 2.1: Dashboard & Authentication (3-4 days)

#### Step 1: Set Up Retailer App Dependencies
Same as customer app, plus:
\`\`\`yaml
dependencies:
  image_picker: ^1.0.5
  qr_code_scanner: ^1.0.1
  fl_chart: ^0.66.0
\`\`\`

#### Step 2: Create Dashboard
Create `apps/retailer_app/lib/screens/dashboard/dashboard_screen.dart`:
- Today's stats (orders, revenue)
- Pending orders count
- Low stock alerts
- Quick actions (add product, view orders)
- Sales chart (last 7 days)

#### Step 3: Authentication
- Reuse auth flow from customer app
- Add role check (RETAILER)
- Store selection if multi-store

#### Success Criteria:
- [ ] Retailer can login with OTP
- [ ] Dashboard shows today's metrics
- [ ] Dashboard shows alerts

---

### Sprint 2.2: Order Management (3-4 days)

#### Step 1: Orders List
Create `apps/retailer_app/lib/screens/orders/orders_screen.dart`:
- Tabs: New, Confirmed, Packed, Out for Delivery
- Order cards with customer info
- Accept/Reject buttons for new orders
- Status update buttons

#### Step 2: Order Details
Create `apps/retailer_app/lib/screens/orders/order_details_screen.dart`:
- Customer details
- Items to pack
- Delivery address
- Payment status
- Mark as packed button
- Assign delivery partner

#### Success Criteria:
- [ ] Retailer receives new order notifications
- [ ] Retailer can accept/reject orders
- [ ] Retailer can update order status
- [ ] Retailer can coordinate with delivery partner

---

### Sprint 2.3: Product Management (4-5 days)

#### Step 1: Products List
Create `apps/retailer_app/lib/screens/products/products_screen.dart`:
- Search products
- Filter by category
- Stock status indicator
- Quick stock update
- Add product button

#### Step 2: Add/Edit Product
Create `apps/retailer_app/lib/screens/products/product_form_screen.dart`:
- Product name, description
- Category selection
- Price, MRP
- Stock quantity
- Unit (kg, pack, etc.)
- Image upload
- Barcode scanning

#### Step 3: Bulk Stock Update
Create `apps/retailer_app/lib/screens/products/bulk_stock_update_screen.dart`:
- CSV upload
- Barcode scanner for quick update
- Stock adjustment log

#### Success Criteria:
- [ ] Retailer can add new products
- [ ] Retailer can update stock
- [ ] Retailer can scan barcodes
- [ ] Retailer can upload product images

---

### Sprint 2.4: KYC & Analytics (3-4 days)

#### Step 1: KYC Onboarding
Create `apps/retailer_app/lib/screens/kyc/`:
1. Business info
2. GST details
3. Bank details
4. Document upload
5. Review & submit

#### Step 2: Analytics Screen
Create `apps/retailer_app/lib/screens/analytics/analytics_screen.dart`:
- Sales chart (daily, weekly, monthly)
- Top selling products
- Customer insights
- Revenue breakdown

#### Success Criteria:
- [ ] New retailer can complete KYC
- [ ] Retailer can view sales analytics
- [ ] Retailer can see top products

---

## 🚗 Phase 3: Delivery App (Week 5)

### Sprint 3.1: Delivery Management (5-7 days)

#### Step 1: Home Screen
Create `apps/delivery_app/lib/screens/home/home_screen.dart`:
- Online/Offline toggle
- Available deliveries list
- Accepted deliveries
- Earnings today

#### Step 2: Delivery Details
Create `apps/delivery_app/lib/screens/delivery/delivery_details_screen.dart`:
- Pickup address
- Delivery address
- Items list
- Earnings for this delivery
- Accept delivery button

#### Step 3: Navigation & Tracking
Add Google Maps dependency:
\`\`\`yaml
dependencies:
  google_maps_flutter: ^2.5.0
\`\`\`

Create `apps/delivery_app/lib/screens/delivery/navigation_screen.dart`:
- Map with route
- Turn-by-turn navigation
- Distance and ETA
- Mark as picked up
- Mark as delivered
- Proof of delivery (photo/signature)

#### Step 4: Earnings Screen
Create `apps/delivery_app/lib/screens/earnings/earnings_screen.dart`:
- Today's earnings
- This week/month
- Payout history
- Detailed trip log

#### Success Criteria:
- [ ] Driver can see available deliveries
- [ ] Driver can accept deliveries
- [ ] Driver can navigate to pickup/delivery
- [ ] Driver can update delivery status
- [ ] Driver can view earnings

---

## 🔧 Phase 4: Integration & Polish (Week 6-7)

### Sprint 4.1: Firebase Integration

#### Step 1: Set Up Firebase Project
1. Create Firebase project
2. Add Android app (com.localgrocery.customer_app)
3. Add iOS app
4. Download config files

#### Step 2: Configure FCM
\`\`\`yaml
dependencies:
  firebase_core: ^2.24.0
  firebase_messaging: ^14.7.3
\`\`\`

Implement push notifications:
- Request permission
- Handle foreground messages
- Handle background messages
- Navigate to relevant screen on tap

#### Step 3: Set Up Crashlytics
\`\`\`yaml
dependencies:
  firebase_crashlytics: ^3.4.6
\`\`\`

#### Success Criteria:
- [ ] Push notifications work
- [ ] Crashes are tracked
- [ ] Analytics events logged

---

### Sprint 4.2: Maps Integration

#### Step 1: Configure Google Maps
Add API keys to Android and iOS configs

#### Step 2: Implement Location Features
- Current location detection
- Address geocoding
- Store location on map
- Distance calculation

#### Success Criteria:
- [ ] Maps display correctly
- [ ] Location services work
- [ ] Distance calculations accurate

---

### Sprint 4.3: Testing & Optimization

#### Step 1: Write Tests
- Unit tests for providers
- Widget tests for screens
- Integration tests for critical flows

#### Step 2: Performance Optimization
- Image caching
- List view optimization
- Network request optimization
- Database queries

#### Step 3: Error Handling
- Network error screens
- Empty states
- Loading states
- Retry mechanisms

#### Success Criteria:
- [ ] All critical flows tested
- [ ] App performs smoothly
- [ ] Errors handled gracefully

---

## 📊 Overall Timeline

| Phase | Duration | Deliverable |
|-------|----------|-------------|
| Phase 1: Customer App | 2 weeks | Fully functional customer app |
| Phase 2: Retailer App | 2 weeks | Fully functional retailer app |
| Phase 3: Delivery App | 1 week | Fully functional delivery app |
| Phase 4: Integration | 2 weeks | Production-ready apps |
| **Total** | **7 weeks** | **3 production apps** |

## 🎯 Success Metrics

### Customer App
- [ ] Users can browse products
- [ ] Users can add items to cart
- [ ] Users can complete checkout
- [ ] Users can track orders
- [ ] App crash rate < 0.1%
- [ ] Average page load time < 2s

### Retailer App
- [ ] Retailers can manage products
- [ ] Retailers can process orders
- [ ] Retailers can view analytics
- [ ] Stock updates reflect in real-time

### Delivery App
- [ ] Drivers can accept deliveries
- [ ] Navigation works accurately
- [ ] Status updates sync in real-time
- [ ] Earnings tracked correctly

## 📚 Resources

### Documentation
- [Flutter Documentation](https://docs.flutter.dev/)
- [Riverpod Guide](https://riverpod.dev/)
- [GoRouter Documentation](https://pub.dev/packages/go_router)
- [Firebase Flutter Setup](https://firebase.google.com/docs/flutter/setup)

### Design References
- [Customer App Wireframes](../../wiki/FLUTTER%20WIREFRAMES/CUSTOMER%20APP%20WIREFRAMES.md)
- [Retailer App Wireframes](../../wiki/FLUTTER%20WIREFRAMES/RETAILER%20APP%20WIREFRAMES.md)
- [Delivery App Wireframes](../../wiki/FLUTTER%20WIREFRAMES/DELIVERY%20PARTNER%20APP%20WIREFRAMES.md)

### Backend APIs
- [OpenAPI Specification](../../backend/openapi.yaml)
- [API Overview](../../wiki/Backend/API_Overview.md)

---

## 🚀 Getting Started

1. Read this roadmap completely
2. Set up your development environment
3. Start with Phase 1, Sprint 1.1
4. Complete one sprint before moving to next
5. Test thoroughly after each sprint
6. Document any issues or deviations

**Remember**: Quality over speed. It's better to have one well-tested feature than multiple buggy ones.

Good luck! 🎉
