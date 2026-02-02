# LocalGrocery Flutter App Implementation Plan

**Last Updated:** January 21, 2026  
**Status:** Planning → Implementation  
**Target:** Multi-app architecture (Customer, Retailer, Delivery Partner)

---

## Overview

Based on the completed backend APIs and planning documents (Requirements.md, Mobile flows, Wireframes), we're building **three Flutter mobile applications** in a monorepo structure with shared core libraries.

### Apps to Build
1. **Customer App** - Browse, order, track
2. **Retailer App** - Inventory, orders, earnings
3. **Delivery Partner App** - Accept deliveries, navigate, complete

---

## Architecture Strategy

### Monorepo Structure
```
frontend/flutter/
├── apps/
│   ├── customer_app/          # Customer-facing app
│   ├── retailer_app/          # Retailer/store management app
│   └── delivery_app/          # Delivery partner app
├── packages/
│   ├── core/                  # Shared utilities, constants
│   ├── models/                # Shared data models
│   ├── api_client/            # HTTP client, API services
│   ├── ui_components/         # Shared widgets, theme
│   └── local_storage/         # Hive/SQLite wrappers
└── docs/
```

### Tech Stack
- **Flutter:** Latest stable (3.x)
- **State Management:** Riverpod 2.x (preferred) or Bloc
- **HTTP Client:** Dio + Retrofit
- **Local Storage:** Hive (cache) + SQLite (offline data)
- **Navigation:** Go Router
- **Maps:** Google Maps Flutter / Mapbox
- **Push Notifications:** Firebase Cloud Messaging
- **Payments:** Razorpay Flutter / Cashfree Flutter
- **Image Handling:** cached_network_image
- **Internationalization:** flutter_localizations + intl

---

## Implementation Phases

### Phase 1: Foundation & Setup (Week 1)
**Goal:** Project scaffolding, core architecture, shared packages

**Tasks:**
- [x] Create monorepo structure
- [ ] Initialize 3 Flutter apps (customer, retailer, delivery)
- [ ] Set up shared packages (core, models, api_client, ui_components)
- [ ] Configure pubspec.yaml for each app
- [ ] Set up development environment (linting, formatting)
- [ ] Create theme system (colors, typography, spacing)
- [ ] Implement API client with interceptors (JWT, refresh token)
- [ ] Set up error handling and logging

**Deliverables:**
- Runnable skeleton apps
- Shared theme and components library
- API client connected to backend services

---

### Phase 2: Authentication & Onboarding (Week 1-2)
**Goal:** OTP-based login, role detection, location permission

**Customer App:**
- Splash screen with brand identity
- Phone number input screen
- OTP verification (auto-read SMS)
- Location permission flow
- JWT token storage and refresh logic

**Retailer App:**
- Same OTP flow with role detection
- KYC status check
- Redirect to KYC completion if pending

**Delivery App:**
- Basic OTP login
- Profile setup

**Shared Components:**
- OTP input widget
- Phone number input
- Loading states
- Error dialogs

**API Integration:**
- `/auth/otp/send`
- `/auth/otp/verify`
- `/auth/refresh-token`
- `/users/me`

---

### Phase 3: Customer App - Core Shopping Flow (Week 2-3)
**Goal:** Browse, search, add to cart, checkout

**Screens:**
1. **Home Screen**
   - Bottom navigation (Home, Orders, Wallet, Profile)
   - Location selector
   - Category chips
   - Nearby stores carousel
   - Product recommendations

2. **Search Screen**
   - Text + voice search
   - Filters (price, brand, distance, availability)
   - Recent searches

3. **Store Detail & Product Listing**
   - Store info header
   - Category tabs
   - Product grid with "Add to Cart"
   - Sticky cart CTA

4. **Product Detail**
   - Image carousel
   - Variant selector
   - Quantity stepper
   - Add to cart

5. **Cart Screen**
   - Store-wise grouping
   - Item quantity controls
   - Coupon application
   - Bill breakdown

6. **Checkout Flow**
   - Address selection/add
   - Delivery slot picker
   - Payment method selection
   - Place order

**API Integration:**
- `/catalog/categories`
- `/catalog/stores/nearby`
- `/catalog/products/search`
- `/catalog/products/{id}`
- `/cart/*`
- `/orders/create`

---

### Phase 4: Customer App - Payments & Orders (Week 3-4)
**Goal:** Payment integration, order tracking, history

**Screens:**
1. **Payment Gateway Integration**
   - Razorpay SDK integration
   - Cashfree fallback
   - UPI, cards, wallets, COD
   - Payment status handling

2. **Order Tracking**
   - Real-time status timeline
   - Live map with rider location
   - ETA updates
   - Call rider/store

3. **Order History**
   - Past orders list
   - Order details
   - Reorder functionality
   - Invoice download

4. **Wallet & Loyalty**
   - Wallet balance
   - Transaction history
   - Points/rewards
   - Referral program

**API Integration:**
- `/payments/initiate`
- `/payments/verify`
- `/orders/{id}`
- `/orders/track/{id}`
- `/wallet/balance`
- `/wallet/transactions`

---

### Phase 5: Retailer App - Order Management (Week 4-5)
**Goal:** Receive orders, manage inventory, track earnings

**Screens:**
1. **Retailer Home**
   - Bottom nav: Orders, Inventory, Earnings, Profile
   - Store status toggle (Open/Closed)
   - Today's summary

2. **Orders Screen**
   - Tabs: New, In Progress, Completed
   - Order cards with quick actions
   - Accept/Reject orders

3. **Order Detail**
   - Item list
   - Customer info
   - Action buttons (Pack, Ready, Handover)
   - Payment status

4. **Inventory Management**
   - Product list with stock counts
   - Low stock warnings
   - Add/Edit products
   - Barcode scanning
   - Price updates

5. **Earnings & Settlements**
   - Revenue overview (Today, Week, Month)
   - Commission breakdown
   - Payout status
   - Transaction history

6. **Profile & KYC**
   - Store details
   - KYC document upload
   - Bank account info
   - Settings

**API Integration:**
- `/retailer/orders`
- `/retailer/orders/{id}/accept`
- `/retailer/orders/{id}/reject`
- `/retailer/orders/{id}/update-status`
- `/inventory/*`
- `/retailer/earnings`
- `/retailer/settlements`
- `/retailer/kyc/*`

---

### Phase 6: Delivery Partner App (Week 5-6)
**Goal:** Accept deliveries, navigate, complete orders

**Screens:**
1. **Available Deliveries**
   - Order cards with earnings
   - Pickup/drop locations
   - Distance and estimated time
   - Accept button

2. **Active Delivery**
   - Order details
   - Navigation (Google Maps integration)
   - Call customer/store
   - Pick up confirmation

3. **Delivery Completion**
   - OTP verification
   - Mark delivered
   - Earnings display

4. **Earnings Dashboard**
   - Trip history
   - Total earnings
   - Payout schedule

**API Integration:**
- `/delivery/available-orders`
- `/delivery/accept/{orderId}`
- `/delivery/pickup-confirm/{orderId}`
- `/delivery/complete/{orderId}`
- `/delivery/earnings`

---

### Phase 7: Advanced Features (Week 6-8)

**All Apps:**
- Push notifications (FCM)
- Deep linking
- Offline mode support
- Image caching and compression
- Performance optimization

**Customer App:**
- Voice search integration
- AR product preview (future)
- Social sharing
- Wishlist
- Product reviews

**Retailer App:**
- Bulk inventory upload (CSV)
- Analytics dashboard
- Offer/coupon creation
- Customer insights

**Delivery App:**
- Route optimization
- Batch deliveries
- Earnings analytics

---

### Phase 8: Testing & Quality Assurance (Week 8-9)

**Unit Tests:**
- Business logic (services, repositories)
- State management (providers/blocs)
- Utilities and helpers

**Widget Tests:**
- Critical UI components
- Form validation
- Navigation flows

**Integration Tests:**
- Complete user journeys
- API integration
- Payment flows

**Manual Testing:**
- Device compatibility (Android 8+, iOS 13+)
- Network scenarios (offline, slow 3G)
- Edge cases
- Regional language support

---

### Phase 9: Deployment Preparation (Week 9-10)

**Android:**
- Generate signed APK/AAB
- Play Store listing preparation
- Internal testing track
- Beta release

**iOS:**
- App Store submission preparation
- TestFlight setup
- Beta testing

**CI/CD:**
- GitHub Actions for automated builds
- Fastlane integration
- Automated testing pipeline

---

## Development Standards

### Code Organization
```
lib/
├── main.dart
├── app.dart
├── core/
│   ├── constants/
│   ├── theme/
│   ├── utils/
│   └── errors/
├── data/
│   ├── models/
│   ├── repositories/
│   └── data_sources/
├── domain/
│   ├── entities/
│   └── use_cases/
├── presentation/
│   ├── screens/
│   ├── widgets/
│   └── providers/
└── routes/
```

### Naming Conventions
- **Files:** snake_case (e.g., `home_screen.dart`)
- **Classes:** PascalCase (e.g., `HomeScreen`)
- **Variables/Functions:** camelCase (e.g., `fetchProducts`)
- **Constants:** UPPER_SNAKE_CASE (e.g., `API_BASE_URL`)

### State Management Pattern (Riverpod)
```dart
// Provider
final productsProvider = StateNotifierProvider<ProductsNotifier, AsyncValue<List<Product>>>((ref) {
  return ProductsNotifier(ref.read(apiClientProvider));
});

// Notifier
class ProductsNotifier extends StateNotifier<AsyncValue<List<Product>>> {
  ProductsNotifier(this._apiClient) : super(const AsyncValue.loading());
  
  final ApiClient _apiClient;
  
  Future<void> fetchProducts() async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() => _apiClient.getProducts());
  }
}

// UI
ref.watch(productsProvider).when(
  data: (products) => ProductList(products: products),
  loading: () => LoadingIndicator(),
  error: (error, stack) => ErrorView(error: error),
);
```

### API Client Pattern
```dart
@RestApi(baseUrl: "")
abstract class ApiClient {
  factory ApiClient(Dio dio, {String baseUrl}) = _ApiClient;
  
  @POST("/auth/otp/send")
  Future<ApiResponse<void>> sendOtp(@Body() SendOtpRequest request);
  
  @POST("/auth/otp/verify")
  Future<ApiResponse<AuthResponse>> verifyOtp(@Body() VerifyOtpRequest request);
  
  @GET("/catalog/products")
  Future<ApiResponse<List<Product>>> getProducts(@Queries() Map<String, dynamic> queries);
}
```

### Error Handling
```dart
class AppException implements Exception {
  final String message;
  final int? statusCode;
  final String? errorCode;
  
  AppException(this.message, {this.statusCode, this.errorCode});
}

// Usage
try {
  await apiClient.sendOtp(request);
} on DioException catch (e) {
  throw AppException(
    e.response?.data['message'] ?? 'Network error',
    statusCode: e.response?.statusCode,
  );
}
```

---

## Dependencies

### Core Dependencies
```yaml
dependencies:
  flutter:
    sdk: flutter
  
  # State Management
  flutter_riverpod: ^2.4.0
  riverpod_annotation: ^2.3.0
  
  # HTTP & API
  dio: ^5.4.0
  retrofit: ^4.0.0
  json_annotation: ^4.8.0
  
  # Local Storage
  hive: ^2.2.3
  hive_flutter: ^1.1.0
  sqflite: ^2.3.0
  
  # Navigation
  go_router: ^13.0.0
  
  # UI
  cached_network_image: ^3.3.0
  flutter_svg: ^2.0.9
  lottie: ^3.0.0
  shimmer: ^3.0.0
  
  # Maps
  google_maps_flutter: ^2.5.0
  geolocator: ^10.1.0
  
  # Firebase
  firebase_core: ^2.24.0
  firebase_messaging: ^14.7.0
  firebase_analytics: ^10.7.0
  
  # Payments
  razorpay_flutter: ^1.3.5
  
  # Utilities
  intl: ^0.18.1
  shared_preferences: ^2.2.2
  flutter_secure_storage: ^9.0.0
  image_picker: ^1.0.5
  permission_handler: ^11.1.0
  url_launcher: ^6.2.2
  
dev_dependencies:
  flutter_test:
    sdk: flutter
  
  # Code Generation
  build_runner: ^2.4.7
  riverpod_generator: ^2.3.0
  retrofit_generator: ^8.0.0
  json_serializable: ^6.7.0
  hive_generator: ^2.0.1
  
  # Linting
  flutter_lints: ^3.0.1
  
  # Testing
  mockito: ^5.4.3
  integration_test:
    sdk: flutter
```

---

## Environment Configuration

### Multiple Environments
```dart
// lib/core/config/env_config.dart
enum Environment { dev, staging, production }

class EnvConfig {
  static Environment currentEnv = Environment.dev;
  
  static String get apiBaseUrl {
    switch (currentEnv) {
      case Environment.dev:
        return 'http://localhost:8000/v1';
      case Environment.staging:
        return 'https://staging-api.localgrocery.com/v1';
      case Environment.production:
        return 'https://api.localgrocery.com/v1';
    }
  }
  
  static String get razorpayKey {
    return currentEnv == Environment.production
        ? 'rzp_live_xxxx'
        : 'rzp_test_xxxx';
  }
}
```

---

## Performance Targets

| Metric | Target | Critical Threshold |
|--------|--------|-------------------|
| App Launch Time | <2s | <3s |
| Screen Transition | <300ms | <500ms |
| API Response Handling | <100ms | <200ms |
| Image Load (cached) | <50ms | <100ms |
| Frame Rate | 60 FPS | >50 FPS |
| App Size (Android) | <30 MB | <50 MB |
| Memory Usage | <150 MB | <200 MB |

---

## Success Criteria

### Phase 1 Success
- [x] All 3 apps can be built and run
- [ ] Shared packages accessible from all apps
- [ ] Theme system applied consistently
- [ ] API client can communicate with backend

### Phase 2 Success
- [ ] Users can log in with OTP
- [ ] JWT tokens stored securely
- [ ] Auto token refresh working
- [ ] Role-based navigation (customer/retailer/delivery)

### Phase 3-4 Success (Customer App MVP)
- [ ] Browse products and stores
- [ ] Add items to cart
- [ ] Complete checkout
- [ ] Make payment (Razorpay)
- [ ] Track order status
- [ ] View order history

### Phase 5 Success (Retailer App MVP)
- [ ] View incoming orders
- [ ] Accept/reject orders
- [ ] Update inventory
- [ ] View earnings and settlements

### Phase 6 Success (Delivery App MVP)
- [ ] See available deliveries
- [ ] Accept delivery
- [ ] Navigate to pickup/drop
- [ ] Mark order delivered

---

## Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Backend API changes | High | API versioning, mock data during dev |
| Payment gateway issues | Critical | Dual gateway (Razorpay + Cashfree), sandbox testing |
| Network unreliability | High | Offline-first architecture, local caching |
| Device fragmentation | Medium | Test on min Android 8, iOS 13; graceful degradation |
| Maps API costs | Medium | Implement caching, optimize API calls |
| Push notification delivery | Medium | FCM with fallback to polling |

---

## Timeline Summary

| Phase | Duration | Start Date | End Date |
|-------|----------|------------|----------|
| Phase 1: Foundation | 1 week | Jan 21 | Jan 27 |
| Phase 2: Auth & Onboarding | 1 week | Jan 27 | Feb 3 |
| Phase 3: Customer Shopping | 1 week | Feb 3 | Feb 10 |
| Phase 4: Payments & Orders | 1 week | Feb 10 | Feb 17 |
| Phase 5: Retailer App | 1 week | Feb 17 | Feb 24 |
| Phase 6: Delivery App | 1 week | Feb 24 | Mar 3 |
| Phase 7: Advanced Features | 2 weeks | Mar 3 | Mar 17 |
| Phase 8: Testing & QA | 1 week | Mar 17 | Mar 24 |
| Phase 9: Deployment Prep | 1 week | Mar 24 | Mar 31 |
| **Total** | **10 weeks** | **Jan 21** | **Mar 31** |

---

## Next Steps

1. **Immediate:** Initialize Flutter project structure
2. **Day 1-2:** Set up shared packages and API client
3. **Day 3-5:** Implement authentication flow
4. **Week 2:** Start customer app core screens

---

## References

- [Requirements.md](wiki/Product/Requirements.md)
- [Customer App Flows](wiki/Mobile/Customer_App_Flows.md)
- [Retailer App Flows](wiki/Mobile/Retailer_App_Flows.md)
- [Delivery App Flows](wiki/Mobile/Delivery_App_Flows.md)
- [Customer Wireframes](wiki/FLUTTER%20WIREFRAMES/CUSTOMER%20APP%20WIREFRAMES.md)
- [Retailer Wireframes](wiki/FLUTTER%20WIREFRAMES/RETAILER%20APP%20WIREFRAMES.md)
- [Delivery Wireframes](wiki/FLUTTER%20WIREFRAMES/DELIVERY%20PARTNER%20APP%20WIREFRAMES.md)
- [Backend API Contracts](backend/openapi.yaml)

---

**Status:** ✅ Plan Complete → Ready for Implementation
