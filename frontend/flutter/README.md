# LocalGrocery Flutter Apps

Multi-app Flutter monorepo for LocalGrocery marketplace platform.

## Project Structure

```
frontend/flutter/
├── apps/
│   ├── customer_app/          # Customer-facing mobile app
│   ├── retailer_app/          # Retailer/store management app
│   └── delivery_app/          # Delivery partner app
├── packages/
│   ├── core/                  # Shared utilities, constants, config
│   ├── models/                # Shared data models
│   ├── api_client/            # HTTP client, API services
│   ├── ui_components/         # Shared widgets, theme
│   └── local_storage/         # Hive/SQLite wrappers
└── docs/                      # Additional documentation
```

## Apps

### 1. Customer App
Browse stores, order groceries, track deliveries, manage wallet.

**Features:**
- OTP-based authentication
- Store and product search
- Multi-store cart
- Multiple payment methods
- Real-time order tracking
- Wallet and loyalty points

### 2. Retailer App
Manage inventory, process orders, track earnings.

**Features:**
- Order management (accept/reject/pack)
- Inventory control
- Product management
- Earnings dashboard
- KYC verification
- Settlement tracking

### 3. Delivery Partner App
Accept deliveries, navigate routes, complete orders.

**Features:**
- Available delivery list
- Route navigation
- Order pickup/delivery confirmation
- Earnings tracking

## Setup Instructions

### Prerequisites
- Flutter SDK 3.16.0 or higher
- Dart 3.2.0 or higher
- Android Studio / VS Code with Flutter extensions
- Xcode (for iOS development on macOS)

### Installation

1. **Install Flutter:**
   ```bash
   # Visit https://flutter.dev/docs/get-started/install
   # Verify installation
   flutter doctor
   ```

2. **Clone Repository:**
   ```bash
   git clone <repository-url>
   cd LocalGrocery/frontend/flutter
   ```

3. **Get Dependencies:**
   ```bash
   # For each app
   cd apps/customer_app
   flutter pub get
   
   cd ../retailer_app
   flutter pub get
   
   cd ../delivery_app
   flutter pub get
   
   # For each package
   cd ../../packages/core
   flutter pub get
   # ... repeat for other packages
   ```

4. **Run Code Generation:**
   ```bash
   # In each app/package that uses code generation
   flutter pub run build_runner build --delete-conflicting-outputs
   ```

### Running Apps

#### Customer App
```bash
cd apps/customer_app
flutter run
```

#### Retailer App
```bash
cd apps/retailer_app
flutter run
```

#### Delivery App
```bash
cd apps/delivery_app
flutter run
```

### Environment Configuration

Create `.env` files in each app directory:

```env
# .env.dev
API_BASE_URL=http://localhost:8000/v1
RAZORPAY_KEY=rzp_test_xxxxx
GOOGLE_MAPS_API_KEY=xxxxx

# .env.staging
API_BASE_URL=https://staging-api.localgrocery.com/v1
RAZORPAY_KEY=rzp_test_xxxxx
GOOGLE_MAPS_API_KEY=xxxxx

# .env.production
API_BASE_URL=https://api.localgrocery.com/v1
RAZORPAY_KEY=rzp_live_xxxxx
GOOGLE_MAPS_API_KEY=xxxxx
```

## Development

### Code Generation
Many packages use code generation (Riverpod, Retrofit, JSON serialization):

```bash
# Watch mode (auto-regenerate on file changes)
flutter pub run build_runner watch

# One-time generation
flutter pub run build_runner build --delete-conflicting-outputs
```

### Linting & Formatting
```bash
# Analyze code
flutter analyze

# Format code
flutter format lib/

# Run both
flutter analyze && flutter format lib/
```

### Testing
```bash
# Unit tests
flutter test

# Integration tests
flutter test integration_test/

# With coverage
flutter test --coverage
```

## Build & Deployment

### Android

#### Debug APK
```bash
flutter build apk --debug
```

#### Release APK
```bash
flutter build apk --release
```

#### App Bundle (for Play Store)
```bash
flutter build appbundle --release
```

### iOS

#### Debug Build
```bash
flutter build ios --debug
```

#### Release Build
```bash
flutter build ios --release
```

## Architecture

### State Management
Using **Riverpod 2.x** for reactive state management.

```dart
// Provider definition
final productsProvider = FutureProvider<List<Product>>((ref) async {
  final apiClient = ref.read(apiClientProvider);
  return apiClient.getProducts();
});

// Usage in UI
ref.watch(productsProvider).when(
  data: (products) => ProductList(products: products),
  loading: () => LoadingIndicator(),
  error: (error, stack) => ErrorView(error: error),
);
```

### API Communication
Using **Dio + Retrofit** for type-safe API calls.

```dart
@RestApi(baseUrl: "")
abstract class ApiClient {
  factory ApiClient(Dio dio) = _ApiClient;
  
  @GET("/products")
  Future<List<Product>> getProducts();
}
```

### Navigation
Using **Go Router** for declarative routing.

```dart
final router = GoRouter(
  routes: [
    GoRoute(
      path: '/',
      builder: (context, state) => HomeScreen(),
    ),
    GoRoute(
      path: '/product/:id',
      builder: (context, state) => ProductDetailScreen(
        productId: state.params['id']!,
      ),
    ),
  ],
);
```

### Local Storage
- **Hive:** Lightweight key-value store for caching
- **SQLite:** Structured data for offline support
- **Secure Storage:** Sensitive data (tokens, credentials)

## Shared Packages

### core
Common utilities, constants, extensions, error handling.

### models
Shared data models (User, Product, Order, etc.) with JSON serialization.

### api_client
HTTP client configuration, API service definitions, interceptors.

### ui_components
Reusable widgets, theme configuration, design tokens.

### local_storage
Database helpers, cache managers, secure storage wrappers.

## Contributing

1. Create a feature branch
2. Make changes
3. Run tests and linters
4. Submit pull request

## Resources

- [Flutter Documentation](https://flutter.dev/docs)
- [Riverpod Documentation](https://riverpod.dev)
- [Go Router Documentation](https://pub.dev/packages/go_router)
- [Backend API Documentation](../../backend/openapi.yaml)

## License

Proprietary - LocalGrocery Platform
