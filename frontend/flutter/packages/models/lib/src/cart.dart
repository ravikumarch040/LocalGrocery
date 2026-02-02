import 'product.dart';

/// Cart model
class Cart {
  final String id;
  final String userId;
  final List<CartItem> items;
  final double subtotal;
  final double discount;
  final double deliveryFee;
  final double platformFee;
  final double total;
  final String? couponCode;

  Cart({
    required this.id,
    required this.userId,
    required this.items,
    required this.subtotal,
    this.discount = 0,
    this.deliveryFee = 0,
    this.platformFee = 0,
    required this.total,
    this.couponCode,
  });

  factory Cart.fromJson(Map<String, dynamic> json) {
    return Cart(
      id: json['id'] as String,
      userId: json['user_id'] as String,
      items: (json['items'] as List)
          .map((item) => CartItem.fromJson(item))
          .toList(),
      subtotal: (json['subtotal'] as num).toDouble(),
      discount: (json['discount'] as num?)?.toDouble() ?? 0,
      deliveryFee: (json['delivery_fee'] as num?)?.toDouble() ?? 0,
      platformFee: (json['platform_fee'] as num?)?.toDouble() ?? 0,
      total: (json['total'] as num).toDouble(),
      couponCode: json['coupon_code'] as String?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'user_id': userId,
      'items': items.map((item) => item.toJson()).toList(),
      'subtotal': subtotal,
      'discount': discount,
      'delivery_fee': deliveryFee,
      'platform_fee': platformFee,
      'total': total,
      'coupon_code': couponCode,
    };
  }

  int get itemCount => items.fold(0, (sum, item) => sum + item.quantity);
  bool get isEmpty => items.isEmpty;
  bool get isNotEmpty => items.isNotEmpty;

  /// Group items by store
  Map<String, List<CartItem>> get itemsByStore {
    final Map<String, List<CartItem>> grouped = {};
    for (final item in items) {
      if (!grouped.containsKey(item.storeId)) {
        grouped[item.storeId] = [];
      }
      grouped[item.storeId]!.add(item);
    }
    return grouped;
  }
}

/// Cart item model
class CartItem {
  final String id;
  final String productId;
  final String storeId;
  final Product product;
  final int quantity;
  final double price;
  final double total;

  CartItem({
    required this.id,
    required this.productId,
    required this.storeId,
    required this.product,
    required this.quantity,
    required this.price,
    required this.total,
  });

  factory CartItem.fromJson(Map<String, dynamic> json) {
    return CartItem(
      id: json['id'] as String,
      productId: json['product_id'] as String,
      storeId: json['store_id'] as String,
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
      'store_id': storeId,
      'product': product.toJson(),
      'quantity': quantity,
      'price': price,
      'total': total,
    };
  }
}
