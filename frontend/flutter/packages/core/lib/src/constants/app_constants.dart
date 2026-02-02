/// Application-wide constants
class AppConstants {
  AppConstants._();

  // App Info
  static const String appName = 'LocalGrocery';
  static const String appVersion = '1.0.0';
  
  // Storage Keys
  static const String keyAccessToken = 'access_token';
  static const String keyRefreshToken = 'refresh_token';
  static const String keyUserId = 'user_id';
  static const String keyUserRole = 'user_role';
  static const String keyUserPhone = 'user_phone';
  static const String keyLocationPermission = 'location_permission_granted';
  static const String keySelectedLanguage = 'selected_language';
  static const String keyThemeMode = 'theme_mode';
  static const String keyFcmToken = 'fcm_token';
  
  // User Roles
  static const String roleCustomer = 'CUSTOMER';
  static const String roleRetailer = 'RETAILER';
  static const String roleDelivery = 'DELIVERY_PARTNER';
  static const String roleAdmin = 'ADMIN';
  
  // Order Status
  static const String orderPlaced = 'PLACED';
  static const String orderConfirmed = 'CONFIRMED';
  static const String orderPacked = 'PACKED';
  static const String orderOutForDelivery = 'OUT_FOR_DELIVERY';
  static const String orderDelivered = 'DELIVERED';
  static const String orderCancelled = 'CANCELLED';
  
  // Payment Status
  static const String paymentPending = 'PENDING';
  static const String paymentPaid = 'PAID';
  static const String paymentFailed = 'FAILED';
  static const String paymentRefunded = 'REFUNDED';
  
  // Payment Methods
  static const String paymentUpi = 'UPI';
  static const String paymentCard = 'CARD';
  static const String paymentWallet = 'WALLET';
  static const String paymentCod = 'COD';
  static const String paymentBnpl = 'BNPL';
  
  // Validation
  static const int otpLength = 6;
  static const int phoneNumberLength = 10;
  static const int minPasswordLength = 6;
  static const Duration otpResendDelay = Duration(seconds: 30);
  
  // Durations
  static const Duration splashDuration = Duration(seconds: 2);
  static const Duration debounceSearchDuration = Duration(milliseconds: 500);
  static const Duration otpTimeoutDuration = Duration(seconds: 60);
  static const Duration apiTimeout = Duration(seconds: 30);
  static const Duration connectionTimeout = Duration(seconds: 15);
  
  // Error Messages
  static const String networkErrorMessage = 'Network error. Please check your connection.';
  static const String genericErrorMessage = 'Something went wrong. Please try again.';
  static const String serverErrorMessage = 'Server error. Please try again later.';
  static const String unauthorizedMessage = 'Session expired. Please login again.';
  static const String validationErrorMessage = 'Please fill all required fields correctly.';
  static const String apiTimeoutMessage = 'Request timeout. Please try again.';
  
  // Pagination
  static const int defaultPageSize = 20;
  static const int maxPageSize = 100;
  
  // Cache
  static const Duration cacheExpiry = Duration(hours: 1);
  static const Duration imageCacheExpiry = Duration(days: 7);
  
  // Location
  static const double defaultLatitude = 28.6139; // Delhi
  static const double defaultLongitude = 77.2090;
  static const double defaultSearchRadius = 5.0; // km
  
  // UI
  static const double defaultPadding = 16.0;
  static const double defaultBorderRadius = 8.0;
  static const Duration defaultAnimationDuration = Duration(milliseconds: 300);
  
  // Maps
  static const double defaultMapZoom = 14.0;
  static const double defaultMapBearing = 0.0;
  static const double defaultMapTilt = 0.0;
}
