/// Store model
class Store {
  final String id;
  final String name;
  final String? description;
  final String? imageUrl;
  final String ownerId;
  final String? ownerName;
  final String phoneNumber;
  final Address address;
  final double rating;
  final int reviewCount;
  final bool isActive;
  final String kycStatus; // PENDING, APPROVED, REJECTED
  final double deliveryRadius; // in km
  final double minOrderValue;
  final bool acceptingOrders;

  Store({
    required this.id,
    required this.name,
    this.description,
    this.imageUrl,
    required this.ownerId,
    this.ownerName,
    required this.phoneNumber,
    required this.address,
    this.rating = 0,
    this.reviewCount = 0,
    this.isActive = false,
    this.kycStatus = 'PENDING',
    this.deliveryRadius = 5.0,
    this.minOrderValue = 0,
    this.acceptingOrders = false,
  });

  factory Store.fromJson(Map<String, dynamic> json) {
    return Store(
      id: json['id'] as String,
      name: json['name'] as String,
      description: json['description'] as String?,
      imageUrl: json['image_url'] as String?,
      ownerId: json['owner_id'] as String,
      ownerName: json['owner_name'] as String?,
      phoneNumber: json['phone_number'] as String,
      address: Address.fromJson(json['address'] as Map<String, dynamic>),
      rating: (json['rating'] as num?)?.toDouble() ?? 0,
      reviewCount: json['review_count'] as int? ?? 0,
      isActive: json['is_active'] as bool? ?? false,
      kycStatus: json['kyc_status'] as String? ?? 'PENDING',
      deliveryRadius: (json['delivery_radius'] as num?)?.toDouble() ?? 5.0,
      minOrderValue: (json['min_order_value'] as num?)?.toDouble() ?? 0,
      acceptingOrders: json['accepting_orders'] as bool? ?? false,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'description': description,
      'image_url': imageUrl,
      'owner_id': ownerId,
      'owner_name': ownerName,
      'phone_number': phoneNumber,
      'address': address.toJson(),
      'rating': rating,
      'review_count': reviewCount,
      'is_active': isActive,
      'kyc_status': kycStatus,
      'delivery_radius': deliveryRadius,
      'min_order_value': minOrderValue,
      'accepting_orders': acceptingOrders,
    };
  }

  bool get isKycApproved => kycStatus == 'APPROVED';
  bool get isKycPending => kycStatus == 'PENDING';
  bool get isKycRejected => kycStatus == 'REJECTED';
}

/// Store address (using same model as delivery address)
class Address {
  final String id;
  final String userId;
  final String type;
  final String addressLine1;
  final String? addressLine2;
  final String landmark;
  final String city;
  final String state;
  final String pinCode;
  final double latitude;
  final double longitude;
  final bool isDefault;

  Address({
    required this.id,
    required this.userId,
    required this.type,
    required this.addressLine1,
    this.addressLine2,
    required this.landmark,
    required this.city,
    required this.state,
    required this.pinCode,
    required this.latitude,
    required this.longitude,
    this.isDefault = false,
  });

  factory Address.fromJson(Map<String, dynamic> json) {
    return Address(
      id: json['id'] as String,
      userId: json['user_id'] as String,
      type: json['type'] as String,
      addressLine1: json['address_line1'] as String,
      addressLine2: json['address_line2'] as String?,
      landmark: json['landmark'] as String,
      city: json['city'] as String,
      state: json['state'] as String,
      pinCode: json['pin_code'] as String,
      latitude: (json['latitude'] as num).toDouble(),
      longitude: (json['longitude'] as num).toDouble(),
      isDefault: json['is_default'] as bool? ?? false,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'user_id': userId,
      'type': type,
      'address_line1': addressLine1,
      'address_line2': addressLine2,
      'landmark': landmark,
      'city': city,
      'state': state,
      'pin_code': pinCode,
      'latitude': latitude,
      'longitude': longitude,
      'is_default': isDefault,
    };
  }

  String get fullAddress {
    final parts = [
      addressLine1,
      if (addressLine2 != null) addressLine2,
      landmark,
      city,
      state,
      pinCode,
    ];
    return parts.join(', ');
  }
}
