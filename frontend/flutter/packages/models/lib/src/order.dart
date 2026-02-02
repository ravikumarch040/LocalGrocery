import 'product.dart';

/// Order model
class Order {
  final String id;
  final String customerId;
  final String storeId;
  final List<OrderItem> items;
  final String status; // PLACED, CONFIRMED, PACKED, OUT_FOR_DELIVERY, DELIVERED, CANCELLED
  final String paymentStatus; // PENDING, PAID, REFUNDED
  final String paymentMethod;
  final double subtotal;
  final double discount;
  final double deliveryFee;
  final double platformFee;
  final double total;
  final String? deliveryInstructions;
  final Address deliveryAddress;
  final DateTime createdAt;
  final DateTime? confirmedAt;
  final DateTime? deliveredAt;

  Order({
    required this.id,
    required this.customerId,
    required this.storeId,
    required this.items,
    required this.status,
    required this.paymentStatus,
    required this.paymentMethod,
    required this.subtotal,
    this.discount = 0,
    this.deliveryFee = 0,
    this.platformFee = 0,
    required this.total,
    this.deliveryInstructions,
    required this.deliveryAddress,
    required this.createdAt,
    this.confirmedAt,
    this.deliveredAt,
  });

  factory Order.fromJson(Map<String, dynamic> json) {
    return Order(
      id: json['id'] as String,
      customerId: json['customer_id'] as String,
      storeId: json['store_id'] as String,
      items: (json['items'] as List)
          .map((item) => OrderItem.fromJson(item))
          .toList(),
      status: json['status'] as String,
      paymentStatus: json['payment_status'] as String,
      paymentMethod: json['payment_method'] as String,
      subtotal: (json['subtotal'] as num).toDouble(),
      discount: (json['discount'] as num?)?.toDouble() ?? 0,
      deliveryFee: (json['delivery_fee'] as num?)?.toDouble() ?? 0,
      platformFee: (json['platform_fee'] as num?)?.toDouble() ?? 0,
      total: (json['total'] as num).toDouble(),
      deliveryInstructions: json['delivery_instructions'] as String?,
      deliveryAddress: Address.fromJson(json['delivery_address'] as Map<String, dynamic>),
      createdAt: DateTime.parse(json['created_at'] as String),
      confirmedAt: json['confirmed_at'] != null
          ? DateTime.parse(json['confirmed_at'] as String)
          : null,
      deliveredAt: json['delivered_at'] != null
          ? DateTime.parse(json['delivered_at'] as String)
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'customer_id': customerId,
      'store_id': storeId,
      'items': items.map((item) => item.toJson()).toList(),
      'status': status,
      'payment_status': paymentStatus,
      'payment_method': paymentMethod,
      'subtotal': subtotal,
      'discount': discount,
      'delivery_fee': deliveryFee,
      'platform_fee': platformFee,
      'total': total,
      'delivery_instructions': deliveryInstructions,
      'delivery_address': deliveryAddress.toJson(),
      'created_at': createdAt.toIso8601String(),
      'confirmed_at': confirmedAt?.toIso8601String(),
      'delivered_at': deliveredAt?.toIso8601String(),
    };
  }

  bool get isPlaced => status == 'PLACED';
  bool get isConfirmed => status == 'CONFIRMED';
  bool get isPacked => status == 'PACKED';
  bool get isOutForDelivery => status == 'OUT_FOR_DELIVERY';
  bool get isDelivered => status == 'DELIVERED';
  bool get isCancelled => status == 'CANCELLED';

  bool get isPaid => paymentStatus == 'PAID';
  bool get isPending => paymentStatus == 'PENDING';
  bool get isRefunded => paymentStatus == 'REFUNDED';
}

/// Order item model
class OrderItem {
  final String id;
  final String productId;
  final Product product;
  final int quantity;
  final double price;
  final double total;

  OrderItem({
    required this.id,
    required this.productId,
    required this.product,
    required this.quantity,
    required this.price,
    required this.total,
  });

  factory OrderItem.fromJson(Map<String, dynamic> json) {
    return OrderItem(
      id: json['id'] as String,
      productId: json['product_id'] as String,
      product: Product.fromJson(json['product'] as Map<String, dynamic>),
      quantity: json['quantity'] as int,
      price: (json['price'] as num).toDouble(),
      total: (json['total'] as num).toDouble(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'product_id': productId,
      'product': product.toJson(),
      'quantity': quantity,
      'price': price,
      'total': total,
    };
  }
}

/// Address model
class Address {
  final String id;
  final String userId;
  final String type; // HOME, WORK, OTHER
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
