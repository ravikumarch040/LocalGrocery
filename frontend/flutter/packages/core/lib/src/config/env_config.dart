import 'package:flutter_dotenv/flutter_dotenv.dart';

/// Environment configuration
enum Environment { dev, staging, production }

class EnvConfig {
  EnvConfig._();

  static Environment _currentEnv = Environment.dev;
  
  static Environment get currentEnv => _currentEnv;
  
  static Future<void> initialize(Environment env) async {
    _currentEnv = env;
    
    // Load appropriate .env file
    final envFile = switch (env) {
      Environment.dev => '.env.dev',
      Environment.staging => '.env.staging',
      Environment.production => '.env.production',
    };
    
    await dotenv.load(fileName: envFile);
  }
  
  // API Configuration
  static String get apiBaseUrl => dotenv.env['API_BASE_URL'] ?? 'http://localhost:8000/v1';
  
  // Payment Gateway Keys
  static String get razorpayKey => dotenv.env['RAZORPAY_KEY'] ?? '';
  static String get cashfreeKey => dotenv.env['CASHFREE_KEY'] ?? '';
  
  // Maps API
  static String get googleMapsApiKey => dotenv.env['GOOGLE_MAPS_API_KEY'] ?? '';
  
  // Firebase
  static String get firebaseApiKey => dotenv.env['FIREBASE_API_KEY'] ?? '';
  static String get firebaseProjectId => dotenv.env['FIREBASE_PROJECT_ID'] ?? '';
  
  // Feature Flags
  static bool get enableAnalytics => dotenv.env['ENABLE_ANALYTICS'] == 'true';
  static bool get enableCrashReporting => dotenv.env['ENABLE_CRASH_REPORTING'] == 'true';
  static bool get enableLogging => _currentEnv != Environment.production;
  
  // App Configuration
  static bool get isProduction => _currentEnv == Environment.production;
  static bool get isDevelopment => _currentEnv == Environment.dev;
  static bool get isStaging => _currentEnv == Environment.staging;
}
