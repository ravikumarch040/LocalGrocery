import 'package:api_client/src/api_client.dart' as api;
import 'package:models/models.dart' as models;

/// Order API service (backend paths under /api/v1/orders)
class OrderService {
  final api.ApiClient _apiClient;

  OrderService(this._apiClient);

  static const String _prefix = '/api/v1/orders';

  /// Map backend OrderResponse to app Order model (total_amount, delivery_address object, item unit_price/total_price/product_name)
  static models.Order _mapOrderResponse(Map<String, dynamic> json) {
    final items = (json['items'] as List<dynamic>?) ?? [];
    final orderItems = items.map((e) {
      final m = e as Map<String, dynamic>;
      final unitPrice = m['unit_price'];
      final totalPrice = m['total_price'];
      return models.OrderItem(
        id: m['id'] as String,
        productId: m['product_id'] as String,
        name: m['product_name'] as String? ?? m['name'] as String? ?? '',
        price: unitPrice is num ? unitPrice.toDouble() : double.tryParse(unitPrice?.toString() ?? '0') ?? 0,
        quantity: (m['quantity'] as num).toInt(),
        subtotal: totalPrice is num ? totalPrice.toDouble() : double.tryParse(totalPrice?.toString() ?? '0') ?? 0,
        createdAt: m['created_at'] != null ? DateTime.tryParse(m['created_at'] as String) : null,
      );
    }).toList();

    String deliveryAddress = '';
    final da = json['delivery_address'];
    if (da is String) {
      deliveryAddress = da;
    } else if (da is Map<String, dynamic>) {
      deliveryAddress = (da['line1'] ?? da['address'] ?? '') as String;
      if (da['line2'] != null) deliveryAddress += ', ${da['line2']}';
      if (da['city'] != null) deliveryAddress += ', ${da['city']}';
      if (da['pincode'] != null) deliveryAddress += ' ${da['pincode']}';
    }

    double _parseMoney(dynamic v) {
      if (v == null) return 0;
      if (v is num) return v.toDouble();
      return double.tryParse(v.toString()) ?? 0;
    }

    return models.Order(
      id: json['id'] as String,
      customerId: json['customer_id'] as String,
      storeId: json['store_id'] as String,
      storeName: json['store_name'] as String? ?? '',
      status: json['status'] as String,
      paymentStatus: json['payment_status'] as String,
      subtotal: _parseMoney(json['subtotal']),
      discount: _parseMoney(json['discount']),
      deliveryFee: _parseMoney(json['delivery_fee']),
      platformFee: _parseMoney(json['platform_fee']),
      total: _parseMoney(json['total_amount'] ?? json['total']),
      deliveryAddress: deliveryAddress,
      deliveryLatitude: null,
      deliveryLongitude: null,
      items: orderItems,
      driverId: json['driver_id'] as String?,
      driverPhone: json['driver_phone'] as String?,
      estimatedDeliveryAt: json['estimated_delivery_at'] != null ? DateTime.tryParse(json['estimated_delivery_at'] as String) : null,
      deliveredAt: json['delivered_at'] != null ? DateTime.tryParse(json['delivered_at'] as String) : null,
      createdAt: json['created_at'] != null ? DateTime.tryParse(json['created_at'] as String) : null,
      updatedAt: json['updated_at'] != null ? DateTime.tryParse(json['updated_at'] as String) : null,
    );
  }

  /// Create new order (BFF-style: address_id + payment_method)
  Future<api.ApiResponse<models.Order>> createOrder({
    required String addressId,
    required String paymentMethod,
    String? deliveryInstructions,
  }) async {
    return await _apiClient.post(
      '$_prefix/',
      body: {
        'address_id': addressId,
        'payment_method': paymentMethod,
        if (deliveryInstructions != null) 'delivery_instructions': deliveryInstructions,
      },
      fromJson: (json) => _mapOrderResponse(json as Map<String, dynamic>),
    );
  }

  /// Create order with full payload (OrderCreate: customer_id, store_id, delivery_address object, items)
  Future<api.ApiResponse<models.Order>> createOrderFromCart({
    required String customerId,
    required String storeId,
    required List<Map<String, dynamic>> items,
    required Map<String, dynamic> deliveryAddress,
    required String paymentMethod,
    String? notes,
  }) async {
    return await _apiClient.post(
      '$_prefix/',
      body: {
        'customer_id': customerId,
        'store_id': storeId,
        'items': items,
        'delivery_address': deliveryAddress,
        'payment_method': paymentMethod,
        if (notes != null && notes.isNotEmpty) 'notes': notes,
      },
      fromJson: (json) => _mapOrderResponse(json as Map<String, dynamic>),
    );
  }

  /// Get order details
  Future<api.ApiResponse<models.Order>> getOrder(String orderId) async {
    return await _apiClient.get(
      '$_prefix/$orderId',
      fromJson: (json) => _mapOrderResponse(json as Map<String, dynamic>),
    );
  }

  /// Get user's orders (optionally filter by store for retailer)
  Future<api.ApiResponse<List<models.Order>>> getOrders({
    int page = 1,
    int pageSize = 20,
    String? status,
    String? storeId,
    String? customerId,
  }) async {
    return await _apiClient.get(
      _prefix,
      queryParams: {
        'page': page.toString(),
        'page_size': pageSize.toString(),
        if (status != null) 'status': status,
        if (storeId != null) 'store_id': storeId,
        if (customerId != null) 'customer_id': customerId,
      },
      fromJson: (json) {
        final list = json is List ? json : (json['orders'] as List? ?? []);
        return list.map((o) => _mapOrderResponse(o as Map<String, dynamic>)).toList();
      },
    );
  }

  /// Update order status (retailer: CONFIRMED, PACKED, etc.)
  Future<api.ApiResponse<models.Order>> updateOrderStatus({
    required String orderId,
    required String status,
  }) async {
    return await _apiClient.put(
      '$_prefix/$orderId',
      body: {'status': status},
      fromJson: (json) => _mapOrderResponse(json as Map<String, dynamic>),
    );
  }

  /// Cancel order (DELETE /api/v1/orders/{order_id})
  Future<api.ApiResponse<void>> cancelOrder({
    required String orderId,
  }) async {
    return await _apiClient.delete(
      '$_prefix/$orderId',
    );
  }

  /// Track order in real-time
  Future<api.ApiResponse<OrderTracking>> trackOrder(String orderId) async {
    return await _apiClient.get(
      '$_prefix/$orderId/track',
      fromJson: (json) => OrderTracking.fromJson(json as Map<String, dynamic>),
    );
  }

  /// Rate order (if backend supports)
  Future<api.ApiResponse<void>> rateOrder({
    required String orderId,
    required int rating,
    String? review,
  }) async {
    return await _apiClient.post(
      '$_prefix/$orderId/rate',
      body: {
        'rating': rating,
        if (review != null) 'review': review,
      },
    );
  }

  /// Reorder (if backend supports)
  Future<api.ApiResponse<models.Cart>> reorder(String orderId) async {
    return await _apiClient.post(
      '$_prefix/$orderId/reorder',
      fromJson: (json) => models.Cart.fromJson(json as Map<String, dynamic>),
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
