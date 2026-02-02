# 📱 LocalGrocery Flutter - Developer Quick Reference

## 🚀 Quick Commands

\`\`\`powershell
# Initial setup
cd frontend/flutter
.\setup.ps1
melos bootstrap

# Run Customer App
cd apps/customer_app
flutter run

# Run with specific device
flutter run -d <device_id>

# Run in release mode
flutter run --release

# Hot reload: Press 'r'
# Hot restart: Press 'R'
# Quit: Press 'q'
\`\`\`

## 📦 Package Management

\`\`\`powershell
# Add dependency to specific app
cd apps/customer_app
flutter pub add package_name

# Add dev dependency
flutter pub add --dev package_name

# Update all packages
melos run get

# Clean and get
melos run clean
melos run get
\`\`\`

## 🏗️ Code Generation

\`\`\`powershell
# Generate code once
cd packages/models
flutter pub run build_runner build --delete-conflicting-outputs

# Watch mode (auto-regenerate)
flutter pub run build_runner watch

# Clean generated files
flutter pub run build_runner clean
\`\`\`

## 🧪 Testing

\`\`\`powershell
# Run all tests
melos run test

# Run tests for specific app
cd apps/customer_app
flutter test

# Run with coverage
flutter test --coverage

# Run specific test file
flutter test test/auth_test.dart
\`\`\`

## 🐛 Debugging

\`\`\`powershell
# Run in debug mode with DevTools
flutter run --enable-devtools

# Check for issues
flutter doctor -v

# Analyze code
flutter analyze

# Format code
flutter format lib/
\`\`\`

## 📱 Device Management

\`\`\`powershell
# List devices
flutter devices

# Run on specific device
flutter run -d chrome
flutter run -d android
flutter run -d ios

# Run on all devices
flutter run -d all
\`\`\`

## 🔧 Common Tasks

### Add a New Screen
1. Create screen file: `lib/screens/screen_name/screen_name_screen.dart`
2. Create provider: `lib/providers/screen_name_provider.dart`
3. Add route in `lib/router.dart`
4. Test screen in isolation

### Create a Provider
\`\`\`dart
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'my_provider.g.dart';

@riverpod
class MyNotifier extends _$MyNotifier {
  @override
  MyState build() {
    // Initialize state
    return MyState();
  }

  void updateState() {
    // Update logic
    state = state.copyWith(/* changes */);
  }
}
\`\`\`

Then run: `flutter pub run build_runner build`

### Add API Endpoint
1. Add method to service in `packages/api_client/lib/src/services/`
2. Update model if needed in `packages/models/lib/src/`
3. Create provider to consume the service
4. Use provider in UI

## 🎨 UI Components

### Common Widgets
\`\`\`dart
// Loading indicator
const CircularProgressIndicator()

// Error message
Text(
  'Error: \$message',
  style: TextStyle(color: Colors.red),
)

// Empty state
Center(
  child: Text('No items found'),
)

// Card with elevation
Card(
  elevation: 4,
  child: /* content */,
)

// List tile
ListTile(
  leading: Icon(Icons.product),
  title: Text('Product Name'),
  subtitle: Text('₹99.00'),
  trailing: Icon(Icons.chevron_right),
  onTap: () { /* action */ },
)
\`\`\`

### Using Riverpod in Widgets
\`\`\`dart
class MyScreen extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final myState = ref.watch(myProvider);
    
    return myState.when(
      data: (data) => /* Show data */,
      loading: () => CircularProgressIndicator(),
      error: (error, stack) => Text('Error: \$error'),
    );
  }
}
\`\`\`

## 🌐 API Integration Pattern

\`\`\`dart
// 1. Create provider for API service
@riverpod
AuthService authService(AuthServiceRef ref) {
  final apiClient = ApiClient(baseUrl: AppConfig.authServiceUrl);
  return AuthService(apiClient);
}

// 2. Create state provider
@riverpod
class Auth extends _$Auth {
  @override
  FutureOr<User?> build() async {
    // Load initial state
    return null;
  }

  Future<void> login(String phone, String otp) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async {
      final service = ref.read(authServiceProvider);
      final response = await service.verifyOTP(
        phoneNumber: phone,
        otp: otp,
      );
      
      if (!response.success) {
        throw Exception(response.message);
      }
      
      return response.data!.user;
    });
  }
}

// 3. Use in UI
class LoginScreen extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final authState = ref.watch(authProvider);
    
    return authState.when(
      data: (user) => HomeScreen(),
      loading: () => CircularProgressIndicator(),
      error: (error, _) => LoginForm(),
    );
  }
}
\`\`\`

## 🗺️ Navigation Pattern

\`\`\`dart
// Define routes
final router = GoRouter(
  routes: [
    GoRoute(
      path: '/',
      builder: (context, state) => SplashScreen(),
    ),
    GoRoute(
      path: '/login',
      builder: (context, state) => LoginScreen(),
    ),
    GoRoute(
      path: '/home',
      builder: (context, state) => HomeScreen(),
    ),
    GoRoute(
      path: '/product/:id',
      builder: (context, state) {
        final productId = state.pathParameters['id']!;
        return ProductDetailsScreen(productId: productId);
      },
    ),
  ],
  redirect: (context, state) {
    // Auth guard
    final isLoggedIn = /* check auth state */;
    final isLoggingIn = state.location == '/login';
    
    if (!isLoggedIn && !isLoggingIn) {
      return '/login';
    }
    return null;
  },
);

// Navigate
context.go('/home');
context.push('/product/123');
context.pop();
\`\`\`

## 🎯 Form Validation

\`\`\`dart
final formKey = GlobalKey<FormState>();

TextFormField(
  validator: Validators.validatePhone,
  decoration: InputDecoration(
    labelText: 'Phone Number',
    hintText: '10-digit mobile number',
  ),
)

// On submit
if (formKey.currentState!.validate()) {
  // Form is valid, proceed
}
\`\`\`

## 💾 Local Storage

\`\`\`dart
// Save token
final prefs = await SharedPreferences.getInstance();
await prefs.setString(AppConstants.tokenKey, token);

// Read token
final token = prefs.getString(AppConstants.tokenKey);

// Delete token
await prefs.remove(AppConstants.tokenKey);

// For sensitive data, use FlutterSecureStorage
final storage = FlutterSecureStorage();
await storage.write(key: 'token', value: token);
final token = await storage.read(key: 'token');
\`\`\`

## 🔔 Push Notifications

\`\`\`dart
// Initialize
await Firebase.initializeApp();
final messaging = FirebaseMessaging.instance;

// Request permission
await messaging.requestPermission();

// Get token
final fcmToken = await messaging.getToken();

// Listen to messages
FirebaseMessaging.onMessage.listen((message) {
  print('Got message: \${message.notification?.title}');
});

// Handle background messages
FirebaseMessaging.onBackgroundMessage(_firebaseMessagingBackgroundHandler);
\`\`\`

## 💳 Payment Integration

\`\`\`dart
// Razorpay
final razorpay = Razorpay();

razorpay.on(Razorpay.EVENT_PAYMENT_SUCCESS, (PaymentSuccessResponse response) {
  // Handle success
});

razorpay.on(Razorpay.EVENT_PAYMENT_ERROR, (PaymentFailureResponse response) {
  // Handle error
});

var options = {
  'key': AppConfig.razorpayKeyId,
  'amount': total * 100, // in paise
  'name': 'LocalGrocery',
  'order_id': orderId,
  'prefill': {
    'contact': phoneNumber,
    'email': email,
  },
};

razorpay.open(options);
\`\`\`

## 📍 Location Services

\`\`\`dart
// Check permission
final permission = await Geolocator.checkPermission();
if (permission == LocationPermission.denied) {
  await Geolocator.requestPermission();
}

// Get current location
final position = await Geolocator.getCurrentPosition();
final latitude = position.latitude;
final longitude = position.longitude;

// Reverse geocode
final placemarks = await placemarkFromCoordinates(latitude, longitude);
final address = placemarks.first;
\`\`\`

## 🎨 Theming

\`\`\`dart
MaterialApp(
  theme: ThemeData(
    primarySwatch: Colors.green,
    fontFamily: GoogleFonts.poppins().fontFamily,
    elevatedButtonTheme: ElevatedButtonThemeData(
      style: ElevatedButton.styleFrom(
        padding: EdgeInsets.symmetric(vertical: 16),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(8),
        ),
      ),
    ),
  ),
)
\`\`\`

## 🐛 Error Handling

\`\`\`dart
try {
  final response = await authService.login(phone, otp);
  if (!response.success) {
    // Show error to user
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(response.message ?? 'Login failed')),
    );
  }
} catch (e) {
  // Handle exception
  print('Error: \$e');
  ScaffoldMessenger.of(context).showSnackBar(
    SnackBar(content: Text('An error occurred')),
  );
}
\`\`\`

## 📊 Useful Packages

| Package | Use Case |
|---------|----------|
| flutter_riverpod | State management |
| go_router | Navigation & routing |
| google_fonts | Typography |
| cached_network_image | Image caching |
| shimmer | Loading placeholders |
| shared_preferences | Simple local storage |
| flutter_secure_storage | Secure storage |
| geolocator | Location services |
| google_maps_flutter | Maps |
| razorpay_flutter | Payments |
| firebase_messaging | Push notifications |
| image_picker | Camera/gallery |
| qr_code_scanner | QR/barcode scanning |
| fl_chart | Charts & graphs |
| intl | Internationalization |
| url_launcher | Open URLs/phones |

## 📝 Code Style

- Use `const` constructors wherever possible
- Prefer `final` over `var`
- Use meaningful variable names
- Add comments for complex logic
- Follow Flutter's official style guide
- Run `flutter format` before committing
- Keep widget build methods small
- Extract widgets when needed

## 🔗 Helpful Links

- [Flutter DevTools](chrome://devtools/)
- [Pub.dev](https://pub.dev/)
- [API Documentation](../../backend/openapi.yaml)
- [Wireframes](../../wiki/FLUTTER%20WIREFRAMES/)
- [Implementation Status](./IMPLEMENTATION_STATUS.md)
- [Development Roadmap](./DEVELOPMENT_ROADMAP.md)

---

**Pro Tip**: Keep this reference handy while developing! Bookmark it in your editor.
