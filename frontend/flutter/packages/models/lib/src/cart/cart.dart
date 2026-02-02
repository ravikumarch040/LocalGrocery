import 'package:json_annotation/json_annotation.dart';
import 'cart_item.dart';

part 'cart.g.dart';

@JsonSerializable()
class Cart {
  final String id;
  @JsonKey(name: 'customer_id')
  final String customerId;
  final List<CartItem> items;
  final double subtotal;
  final double discount;
  @JsonKey(name: 'delivery_fee')
  final double deliveryFee;
  @JsonKey(name: 'platform_fee')
  final double platformFee;
  final double total;
  @JsonKey(name: 'coupon_code')
  final String? couponCode;
  @JsonKey(name: 'coupon_discount')
  final double couponDiscount;
  @JsonKey(name: 'created_at')
  final DateTime? createdAt;
  @JsonKey(name: 'updated_at')
  final DateTime? updatedAt;

  const Cart({
    required this.id,
    required this.customerId,
    required this.items,
    required this.subtotal,
    required this.discount,
    required this.deliveryFee,
    required this.platformFee,
    required this.total,
    this.couponCode,
    required this.couponDiscount,
    this.createdAt,
    this.updatedAt,
  });

  factory Cart.fromJson(Map<String, dynamic> json) => _$CartFromJson(json);
  Map<String, dynamic> toJson() => _$CartToJson(this);

  Cart copyWith({
    String? id,
    String? customerId,
    List<CartItem>? items,
    double? subtotal,
    double? discount,
    double? deliveryFee,
    double? platformFee,
    double? total,
    String? couponCode,
    double? couponDiscount,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) {
    return Cart(
      id: id ?? this.id,
      customerId: customerId ?? this.customerId,
      items: items ?? this.items,
      subtotal: subtotal ?? this.subtotal,
      discount: discount ?? this.discount,
      deliveryFee: deliveryFee ?? this.deliveryFee,
      platformFee: platformFee ?? this.platformFee,
      total: total ?? this.total,
      couponCode: couponCode ?? this.couponCode,
      couponDiscount: couponDiscount ?? this.couponDiscount,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }
}
