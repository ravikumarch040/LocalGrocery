import 'package:api_client/src/api_client.dart' as api;

/// Delivery API service (backend paths under /v1/deliveries and /v1/partners)
class DeliveryService {
  final api.ApiClient _apiClient;

  DeliveryService(this._apiClient);

  static const String _deliveriesPrefix = '/v1/deliveries';
  static const String _partnersPrefix = '/v1/partners';

  /// List deliveries (optional filter by status, partner_id)
  Future<api.ApiResponse<List<DeliveryDto>>> listDeliveries({
    String? status,
    String? partnerId,
    int skip = 0,
    int limit = 50,
  }) async {
    return await _apiClient.get(
      _deliveriesPrefix,
      queryParams: {
        if (status != null) 'status': status,
        if (partnerId != null) 'partner_id': partnerId,
        'skip': skip.toString(),
        'limit': limit.toString(),
      },
      fromJson: (json) {
        final list = json is List ? json : (json['deliveries'] as List? ?? []);
        return list.map((e) => DeliveryDto.fromJson(e as Map<String, dynamic>)).toList();
      },
    );
  }

  /// Get delivery by ID
  Future<api.ApiResponse<DeliveryDto>> getDelivery(String deliveryId) async {
    return await _apiClient.get(
      '$_deliveriesPrefix/$deliveryId',
      fromJson: (json) => DeliveryDto.fromJson(json as Map<String, dynamic>),
    );
  }

  /// Get delivery by order ID
  Future<api.ApiResponse<DeliveryDto>> getDeliveryByOrder(String orderId) async {
    return await _apiClient.get(
      '$_deliveriesPrefix/order/$orderId',
      fromJson: (json) => DeliveryDto.fromJson(json as Map<String, dynamic>),
    );
  }

  /// Assign delivery to partner (accept delivery)
  Future<api.ApiResponse<DeliveryDto>> assignDelivery({
    required String deliveryId,
    required String deliveryPartnerId,
  }) async {
    return await _apiClient.post(
      '$_deliveriesPrefix/$deliveryId/assign',
      body: {'delivery_partner_id': deliveryPartnerId},
      fromJson: (json) => DeliveryDto.fromJson(json as Map<String, dynamic>),
    );
  }

  /// Update delivery status (PICKED_UP, IN_TRANSIT, DELIVERED, etc.)
  Future<api.ApiResponse<DeliveryDto>> updateDeliveryStatus({
    required String deliveryId,
    required String status,
    Map<String, dynamic>? location,
    String? notes,
  }) async {
    return await _apiClient.patch(
      '$_deliveriesPrefix/$deliveryId/status',
      body: {
        'status': status,
        if (location != null) 'location': location,
        if (notes != null) 'notes': notes,
      },
      fromJson: (json) => DeliveryDto.fromJson(json as Map<String, dynamic>),
    );
  }

  /// Get delivery partner by ID
  Future<api.ApiResponse<DeliveryPartnerDto>> getPartner(String partnerId) async {
    return await _apiClient.get(
      '$_partnersPrefix/$partnerId',
      fromJson: (json) => DeliveryPartnerDto.fromJson(json as Map<String, dynamic>),
    );
  }

  /// Update partner status (AVAILABLE, BUSY, OFFLINE)
  Future<api.ApiResponse<DeliveryPartnerDto>> updatePartnerStatus({
    required String partnerId,
    required String status,
  }) async {
    return await _apiClient.patch(
      '$_partnersPrefix/$partnerId/status',
      body: {'status': status},
      fromJson: (json) => DeliveryPartnerDto.fromJson(json as Map<String, dynamic>),
    );
  }

  /// Update partner location
  Future<api.ApiResponse<void>> updatePartnerLocation({
    required String partnerId,
    required double lat,
    required double lng,
    String? address,
  }) async {
    return await _apiClient.patch(
      '$_partnersPrefix/$partnerId/location',
      body: {
        'location': {
          'lat': lat,
          'lng': lng,
          if (address != null) 'address': address,
        },
      },
    );
  }
}

/// Delivery DTO matching backend DeliveryResponse
class DeliveryDto {
  final String id;
  final String orderId;
  final String? deliveryPartnerId;
  final String? partnerName;
  final String? partnerPhone;
  final String status;
  final Map<String, dynamic> pickupLocation;
  final Map<String, dynamic> deliveryLocation;
  final Map<String, dynamic>? currentLocation;
  final double? distanceKm;
  final double? estimatedTimeMinutes;
  final double? actualTimeMinutes;
  final double? deliveryFee;
  final String? deliveryInstructions;
  final String? createdAt;
  final String? updatedAt;

  DeliveryDto({
    required this.id,
    required this.orderId,
    this.deliveryPartnerId,
    this.partnerName,
    this.partnerPhone,
    required this.status,
    required this.pickupLocation,
    required this.deliveryLocation,
    this.currentLocation,
    this.distanceKm,
    this.estimatedTimeMinutes,
    this.actualTimeMinutes,
    this.deliveryFee,
    this.deliveryInstructions,
    this.createdAt,
    this.updatedAt,
  });

  factory DeliveryDto.fromJson(Map<String, dynamic> json) {
    double? parseDouble(dynamic v) {
      if (v == null) return null;
      if (v is num) return v.toDouble();
      return double.tryParse(v.toString());
    }

    return DeliveryDto(
      id: json['id'] as String,
      orderId: json['order_id'] as String,
      deliveryPartnerId: json['delivery_partner_id'] as String?,
      partnerName: json['partner_name'] as String?,
      partnerPhone: json['partner_phone'] as String?,
      status: json['status'] as String,
      pickupLocation: (json['pickup_location'] as Map<String, dynamic>?) ?? {},
      deliveryLocation: (json['delivery_location'] as Map<String, dynamic>?) ?? {},
      currentLocation: json['current_location'] as Map<String, dynamic>?,
      distanceKm: parseDouble(json['distance_km']),
      estimatedTimeMinutes: parseDouble(json['estimated_time_minutes']),
      actualTimeMinutes: parseDouble(json['actual_time_minutes']),
      deliveryFee: parseDouble(json['delivery_fee']),
      deliveryInstructions: json['delivery_instructions'] as String?,
      createdAt: json['created_at']?.toString(),
      updatedAt: json['updated_at']?.toString(),
    );
  }

  String get pickupAddress => pickupLocation['address'] as String? ?? 'Pickup';
  String get deliveryAddress => deliveryLocation['address'] as String? ?? 'Delivery';
}

/// Delivery partner DTO
class DeliveryPartnerDto {
  final String id;
  final String name;
  final String phone;
  final String? email;
  final String vehicleType;
  final String? vehicleNumber;
  final String status;
  final bool isVerified;
  final bool isActive;
  final int totalDeliveries;
  final int successfulDeliveries;
  final double rating;

  DeliveryPartnerDto({
    required this.id,
    required this.name,
    required this.phone,
    this.email,
    required this.vehicleType,
    this.vehicleNumber,
    required this.status,
    required this.isVerified,
    required this.isActive,
    required this.totalDeliveries,
    required this.successfulDeliveries,
    required this.rating,
  });

  factory DeliveryPartnerDto.fromJson(Map<String, dynamic> json) {
    return DeliveryPartnerDto(
      id: json['id'] as String,
      name: json['name'] as String,
      phone: json['phone'] as String,
      email: json['email'] as String?,
      vehicleType: json['vehicle_type'] as String? ?? 'BIKE',
      vehicleNumber: json['vehicle_number'] as String?,
      status: json['status'] as String? ?? 'OFFLINE',
      isVerified: json['is_verified'] as bool? ?? false,
      isActive: json['is_active'] as bool? ?? true,
      totalDeliveries: (json['total_deliveries'] as num?)?.toInt() ?? 0,
      successfulDeliveries: (json['successful_deliveries'] as num?)?.toInt() ?? 0,
      rating: (json['rating'] as num?)?.toDouble() ?? 0,
    );
  }
}
