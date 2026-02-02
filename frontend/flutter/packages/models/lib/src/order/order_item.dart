import 'package:json_annotation/json_annotation.dart';

part 'order_item.g.dart';

@JsonSerializable()
class OrderItem {
  final String id;
  @JsonKey(name: 'product_id')
  final String productId;
  final String name;
  final double price;
  final int quantity;
  final double subtotal;
  @JsonKey(name: 'created_at')
  final DateTime? createdAt;

  const OrderItem({
    required this.id,
    required this.productId,
    required this.name,
    required this.price,
    required this.quantity,
    required this.subtotal,
    this.createdAt,
  });

  factory OrderItem.fromJson(Map<String, dynamic> json) => _$OrderItemFromJson(json);
  Map<String, dynamic> toJson() => _$OrderItemToJson(this);
}
