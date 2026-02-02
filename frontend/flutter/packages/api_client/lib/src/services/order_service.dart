import 'package:api_client/src/api_client.dart' as api;
import 'package:models/models.dart' as models;

/// Order API service
class OrderService {
  final api.ApiClient _apiClient;

  OrderService(this._apiClient);

  /// Create new order (BFF-style: address_id + payment_method)
  Future<api.ApiResponse<models.Order>> createOrder({
    required String addressId,
    required String paymentMethod,
    String? deliveryInstructions,
  }) async {
    return await _apiClient.post(
      '/orders',
      body: {
        'address_id': addressId,
        'payment_method': paymentMethod,
        if (deliveryInstructions != null) 'delivery_instructions': deliveryInstructions,
      },
      fromJson: (json) => models.Order.fromJson(json),
    );
  }

  /// Create order with full payload (for backends that expect OrderCreate: customer_id, store_id, delivery_address, items)
  Future<api.ApiResponse<models.Order>> createOrderFromCart({
    required String customerId,
    required String storeId,
    required List<Map<String, dynamic>> items,
    required Map<String, String> deliveryAddress,
    required String paymentMethod,
    String? notes,
  }) async {
    return await _apiClient.post(
      '/orders',
      body: {
        'customer_id': customerId,
        'store_id': storeId,
        'items': items,
        'delivery_address': deliveryAddress,
        'payment_method': paymentMethod,
        if (notes != null && notes.isNotEmpty) 'notes': notes,
      },
      fromJson: (json) => models.Order.fromJson(json),
    );
  }

  /// Get order details
  Future<api.ApiResponse<models.Order>> getOrder(String orderId) async {
    return await _apiClient.get(
      '/orders/$orderId',
      fromJson: (json) => models.Order.fromJson(json),
    );
  }

  /// Get user's orders
  Future<api.ApiResponse<List<models.Order>>> getOrders({
    int page = 1,
    int pageSize = 20,
    String? status,
  }) async {
    return await _apiClient.get(
      '/orders',
      queryParams: {
        'page': page.toString(),
        'page_size': pageSize.toString(),
        if (status != null) 'status': status,
      },
      fromJson: (json) {
        final orders = json['orders'] as List;
        return orders.map((o) => models.Order.fromJson(o)).toList();
      },
    );
  }

  /// Cancel order
  Future<api.ApiResponse<models.Order>> cancelOrder({
    required String orderId,
    String? reason,
  }) async {
    return await _apiClient.post(
      '/orders/$orderId/cancel',
      body: {
        if (reason != null) 'reason': reason,
      },
      fromJson: (json) => models.Order.fromJson(json),
    );
  }

  /// Track order in real-time
  Future<api.ApiResponse<OrderTracking>> trackOrder(String orderId) async {
    return await _apiClient.get(
      '/orders/$orderId/track',
      fromJson: (json) => OrderTracking.fromJson(json),
    );
  }

  /// Rate order
  Future<api.ApiResponse<void>> rateOrder({
    required String orderId,
    required int rating,
    String? review,
  }) async {
    return await _apiClient.post(
      '/orders/$orderId/rate',
      body: {
        'rating': rating,
        if (review != null) 'review': review,
      },
    );
  }

  /// Reorder (create new order from previous order)
  Future<api.ApiResponse<models.Cart>> reorder(String orderId) async {
    return await _apiClient.post(
      '/orders/$orderId/reorder',
      fromJson: (json) => models.Cart.fromJson(json),
    );
  }
}

/// Order tracking model
class OrderTracking {
  final String orderId;
  final String status;
  final DeliveryPartner? deliveryPartner;
  final Location? currentLocation;
  final String? estimatedDeliveryTime;

  OrderTracking({
    required this.orderId,
    required this.status,
    this.deliveryPartner,
    this.currentLocation,
    this.estimatedDeliveryTime,
  });

  factory OrderTracking.fromJson(Map<String, dynamic> json) {
    return OrderTracking(
      orderId: json['order_id'] as String,
      status: json['status'] as String,
      deliveryPartner: json['delivery_partner'] != null
          ? DeliveryPartner.fromJson(json['delivery_partner'] as Map<String, dynamic>)
          : null,
      currentLocation: json['current_location'] != null
          ? Location.fromJson(json['current_location'] as Map<String, dynamic>)
          : null,
      estimatedDeliveryTime: json['estimated_delivery_time'] as String?,
    );
  }
}

class DeliveryPartner {
  final String id;
  final String name;
  final String phoneNumber;
  final String? vehicleNumber;

  DeliveryPartner({
    required this.id,
    required this.name,
    required this.phoneNumber,
    this.vehicleNumber,
  });

  factory DeliveryPartner.fromJson(Map<String, dynamic> json) {
    return DeliveryPartner(
      id: json['id'] as String,
      name: json['name'] as String,
      phoneNumber: json['phone_number'] as String,
      vehicleNumber: json['vehicle_number'] as String?,
    );
  }
}

class Location {
  final double latitude;
  final double longitude;

  Location({
    required this.latitude,
    required this.longitude,
  });

  factory Location.fromJson(Map<String, dynamic> json) {
    return Location(
      latitude: json['latitude'] as double,
      longitude: json['longitude'] as double,
    );
  }
}
