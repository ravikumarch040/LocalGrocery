import 'package:flutter/foundation.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';

/// Application configuration from environment variables
class AppConfig {
  // Web builds: hardcoded localhost defaults (no .env access)
  // Native builds: read from .env files
  
  static String get apiBaseUrl => kIsWeb ? '' : (dotenv.env['API_BASE_URL'] ?? '');
  static String get apiGatewayUrl => kIsWeb ? '' : (dotenv.env['API_GATEWAY_URL'] ?? '');
  
  // Service endpoints
  static String get authServiceUrl => kIsWeb ? 'http://localhost:8001' : (dotenv.env['AUTH_SERVICE_URL'] ?? '');
  static String get catalogServiceUrl => kIsWeb ? 'http://localhost:8002' : (dotenv.env['CATALOG_SERVICE_URL'] ?? '');
  static String get cartServiceUrl => kIsWeb ? 'http://localhost:8003' : (dotenv.env['CART_SERVICE_URL'] ?? '');
  static String get orderServiceUrl => kIsWeb ? 'http://localhost:8004' : (dotenv.env['ORDER_SERVICE_URL'] ?? '');
  static String get paymentServiceUrl => kIsWeb ? 'http://localhost:8005' : (dotenv.env['PAYMENT_SERVICE_URL'] ?? '');
  static String get inventoryServiceUrl => kIsWeb ? 'http://localhost:8006' : (dotenv.env['INVENTORY_SERVICE_URL'] ?? '');
  static String get deliveryServiceUrl => kIsWeb ? 'http://localhost:8007' : (dotenv.env['DELIVERY_SERVICE_URL'] ?? '');
  static String get notificationServiceUrl => kIsWeb ? 'http://localhost:8008' : (dotenv.env['NOTIFICATION_SERVICE_URL'] ?? '');
  
  // Firebase
  static String get firebaseApiKey => kIsWeb ? '' : (dotenv.env['FIREBASE_API_KEY'] ?? '');
  static String get firebaseProjectId => kIsWeb ? '' : (dotenv.env['FIREBASE_PROJECT_ID'] ?? '');
  static String get firebaseMessagingSenderId => kIsWeb ? '' : (dotenv.env['FIREBASE_MESSAGING_SENDER_ID'] ?? '');
  static String get firebaseAppId => kIsWeb ? '' : (dotenv.env['FIREBASE_APP_ID'] ?? '');
  
  // Maps
  static String get googleMapsApiKey => kIsWeb ? '' : (dotenv.env['GOOGLE_MAPS_API_KEY'] ?? '');
  static String get mapboxAccessToken => kIsWeb ? '' : (dotenv.env['MAPBOX_ACCESS_TOKEN'] ?? '');
  
  // Payment gateways
  static String get razorpayKeyId => kIsWeb ? '' : (dotenv.env['RAZORPAY_KEY_ID'] ?? '');
  static String get cashfreeAppId => kIsWeb ? '' : (dotenv.env['CASHFREE_APP_ID'] ?? '');
  
  // Feature flags
  static bool get enableDebugMode => kIsWeb ? true : (dotenv.env['ENABLE_DEBUG_MODE'] == 'true');
  static bool get enableAnalytics => kIsWeb ? false : (dotenv.env['ENABLE_ANALYTICS'] == 'true');
  static bool get enableCrashReporting => kIsWeb ? false : (dotenv.env['ENABLE_CRASH_REPORTING'] == 'true');
  
  // App settings
  static String get appEnvironment => kIsWeb ? 'dev' : (dotenv.env['APP_ENVIRONMENT'] ?? 'dev');
  static bool get isProduction => appEnvironment == 'production';
  static bool get isStaging => appEnvironment == 'staging';
  static bool get isDevelopment => appEnvironment == 'dev';
  
  /// Initialize configuration
  static Future<void> initialize({String environment = 'dev'}) async {
    // Skip dotenv loading for web builds - .env files aren't bundled
    if (kIsWeb) {
      if (kDebugMode) {
        print('⚠️ Web build detected - skipping .env loading');
        print('✅ Using built-in localhost defaults');
      }
      return;
    }

    // On native platforms (Windows, macOS, Linux, Android, iOS), try to load .env
    try {
      await dotenv.load(fileName: '.env.$environment');
      if (kDebugMode) {
        print('✅ AppConfig initialized for environment: $environment');
      }
    } catch (e) {
      if (kDebugMode) {
        print('⚠️ Failed to load .env.$environment: $e');
        print('⚠️ Continuing with fallback defaults (localhost services)');
      }
    }
  }
}
