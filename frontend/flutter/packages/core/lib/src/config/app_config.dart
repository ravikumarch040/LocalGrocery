import 'package:flutter/foundation.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';

/// Application configuration from environment variables
class AppConfig {
  // Web builds: hardcoded localhost defaults (no .env access)
  // Native builds: read from .env files
  
  /// Safely get environment variable, returning empty string if not initialized
  static String _getEnv(String key, String defaultValue) {
    if (kIsWeb) return defaultValue;
    try {
      return dotenv.env[key] ?? defaultValue;
    } catch (e) {
      // dotenv not initialized, return default
      return defaultValue;
    }
  }
  
  static String get apiBaseUrl => _getEnv('API_BASE_URL', '');
  static String get apiGatewayUrl => _getEnv('API_GATEWAY_URL', '');
  
  // Service endpoints
  static String get authServiceUrl => _getEnv('AUTH_SERVICE_URL', 'http://localhost:8001');
  static String get catalogServiceUrl => _getEnv('CATALOG_SERVICE_URL', 'http://localhost:8002');
  static String get cartServiceUrl => _getEnv('CART_SERVICE_URL', 'http://localhost:8008');
  static String get orderServiceUrl => _getEnv('ORDER_SERVICE_URL', 'http://localhost:8003');
  static String get paymentServiceUrl => _getEnv('PAYMENT_SERVICE_URL', 'http://localhost:8004');
  static String get inventoryServiceUrl => _getEnv('INVENTORY_SERVICE_URL', 'http://localhost:8007');
  static String get deliveryServiceUrl => _getEnv('DELIVERY_SERVICE_URL', 'http://localhost:8005');
  static String get notificationServiceUrl => _getEnv('NOTIFICATION_SERVICE_URL', 'http://localhost:8006');
  
  // Firebase
  static String get firebaseApiKey => _getEnv('FIREBASE_API_KEY', '');
  static String get firebaseProjectId => _getEnv('FIREBASE_PROJECT_ID', '');
  static String get firebaseMessagingSenderId => _getEnv('FIREBASE_MESSAGING_SENDER_ID', '');
  static String get firebaseAppId => _getEnv('FIREBASE_APP_ID', '');
  
  // Maps
  static String get googleMapsApiKey => _getEnv('GOOGLE_MAPS_API_KEY', '');
  static String get mapboxAccessToken => _getEnv('MAPBOX_ACCESS_TOKEN', '');
  
  // Payment gateways
  static String get razorpayKeyId => _getEnv('RAZORPAY_KEY_ID', '');
  static String get cashfreeAppId => _getEnv('CASHFREE_APP_ID', '');
  
  // Feature flags
  static bool get enableDebugMode => kIsWeb ? true : (_getEnv('ENABLE_DEBUG_MODE', 'true') == 'true');
  static bool get enableAnalytics => kIsWeb ? false : (_getEnv('ENABLE_ANALYTICS', 'false') == 'true');
  static bool get enableCrashReporting => kIsWeb ? false : (_getEnv('ENABLE_CRASH_REPORTING', 'false') == 'true');
  
  // App settings
  static String get appEnvironment => _getEnv('APP_ENVIRONMENT', 'dev');
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
      // Try loading from current directory first (for apps)
      await dotenv.load(fileName: '.env.$environment');
      if (kDebugMode) {
        print('✅ AppConfig initialized for environment: $environment');
        print('✅ Loaded .env.$environment from current directory');
      }
    } catch (e) {
      // If that fails, try loading from parent directory (for packages)
      try {
        await dotenv.load(fileName: '../.env.$environment');
        if (kDebugMode) {
          print('✅ AppConfig initialized for environment: $environment');
          print('✅ Loaded .env.$environment from parent directory');
        }
      } catch (e2) {
        if (kDebugMode) {
          print('⚠️ Failed to load .env.$environment: $e');
          print('⚠️ Continuing with fallback defaults (localhost services)');
        }
      }
    }
  }
}
