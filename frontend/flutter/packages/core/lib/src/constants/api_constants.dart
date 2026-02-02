/// API endpoint constants
class ApiConstants {
  ApiConstants._();

  // Base URL - overridden by environment config
  static const String defaultBaseUrl = 'http://localhost:8000';
  
  // API Version
  static const String apiVersion = 'v1';
  
  // Timeout durations
  static const Duration connectTimeout = Duration(seconds: 30);
  static const Duration receiveTimeout = Duration(seconds: 30);
  static const Duration sendTimeout = Duration(seconds: 30);
  
  // Auth endpoints
  static const String authSendOtp = '/auth/otp/send';
  static const String authVerifyOtp = '/auth/otp/verify';
  static const String authRefreshToken = '/auth/refresh-token';
  static const String userProfile = '/users/me';
  
  // Catalog endpoints
  static const String categories = '/catalog/categories';
  static const String stores = '/catalog/stores';
  static const String storesNearby = '/catalog/stores/nearby';
  static const String products = '/catalog/products';
  static const String productSearch = '/catalog/products/search';
  
  // Cart endpoints
  static const String cart = '/cart';
  static const String cartAdd = '/cart/add';
  static const String cartUpdate = '/cart/update';
  static const String cartRemove = '/cart/remove';
  static const String cartClear = '/cart/clear';
  
  // Order endpoints
  static const String orders = '/orders';
  static const String orderCreate = '/orders/create';
  static const String orderTrack = '/orders/track';
  
  // Payment endpoints
  static const String paymentInitiate = '/payments/initiate';
  static const String paymentVerify = '/payments/verify';
  static const String paymentWebhook = '/payments/webhook';
  
  // Wallet endpoints
  static const String wallet = '/wallet';
  static const String walletBalance = '/wallet/balance';
  static const String walletTransactions = '/wallet/transactions';
  
  // Retailer endpoints
  static const String retailerOrders = '/retailer/orders';
  static const String retailerOrderAccept = '/retailer/orders/{id}/accept';
  static const String retailerOrderReject = '/retailer/orders/{id}/reject';
  static const String retailerOrderUpdateStatus = '/retailer/orders/{id}/update-status';
  static const String retailerEarnings = '/retailer/earnings';
  static const String retailerSettlements = '/retailer/settlements';
  static const String retailerKyc = '/retailer/kyc';
  
  // Inventory endpoints
  static const String inventory = '/inventory';
  static const String inventoryProducts = '/inventory/products';
  static const String inventoryReserve = '/inventory/reserve';
  
  // Delivery endpoints
  static const String deliveryAvailableOrders = '/delivery/available-orders';
  static const String deliveryAccept = '/delivery/accept';
  static const String deliveryPickupConfirm = '/delivery/pickup-confirm';
  static const String deliveryComplete = '/delivery/complete';
  static const String deliveryEarnings = '/delivery/earnings';
  
  // Notification endpoints
  static const String notificationRegisterDevice = '/notifications/register-device';
  static const String notificationPreferences = '/notifications/preferences';
}
