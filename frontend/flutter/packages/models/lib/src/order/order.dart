import 'package:json_annotation/json_annotation.dart';
import 'order_item.dart';

part 'order.g.dart';

@JsonSerializable()
class Order {
  final String id;
  @JsonKey(name: 'customer_id')
  final String customerId;
  @JsonKey(name: 'store_id')
  final String storeId;
  @JsonKey(name: 'store_name')
  final String storeName;
  final String status;
  @JsonKey(name: 'payment_status')
  final String paymentStatus;
  final double subtotal;
  final double discount;
  @JsonKey(name: 'delivery_fee')
  final double deliveryFee;
  @JsonKey(name: 'platform_fee')
  final double platformFee;
  final double total;
  @JsonKey(name: 'delivery_address')
  final String deliveryAddress;
  @JsonKey(name: 'delivery_latitude')
  final double? deliveryLatitude;
  @JsonKey(name: 'delivery_longitude')
  final double? deliveryLongitude;
  final List<OrderItem> items;
  @JsonKey(name: 'driver_id')
  final String? driverId;
  @JsonKey(name: 'driver_phone')
  final String? driverPhone;
  @JsonKey(name: 'estimated_delivery_at')
  final DateTime? estimatedDeliveryAt;
  @JsonKey(name: 'delivered_at')
  final DateTime? deliveredAt;
  @JsonKey(name: 'created_at')
  final DateTime? createdAt;
  @JsonKey(name: 'updated_at')
  final DateTime? updatedAt;

  const Order({
    required this.id,
    required this.customerId,
    required this.storeId,
    required this.storeName,
    required this.status,
    required this.paymentStatus,
    required this.subtotal,
    required this.discount,
    required this.deliveryFee,
    required this.platformFee,
    required this.total,
    required this.deliveryAddress,
    this.deliveryLatitude,
    this.deliveryLongitude,
    required this.items,
    this.driverId,
    this.driverPhone,
    this.estimatedDeliveryAt,
    this.deliveredAt,
    this.createdAt,
    this.updatedAt,
  });

  factory Order.fromJson(Map<String, dynamic> json) => _$OrderFromJson(json);
  Map<String, dynamic> toJson() => _$OrderToJson(this);

  Order copyWith({
    String? id,
    String? customerId,
    String? storeId,
    String? storeName,
    String? status,
    String? paymentStatus,
    double? subtotal,
    double? discount,
    double? deliveryFee,
    double? platformFee,
    double? total,
    String? deliveryAddress,
    double? deliveryLatitude,
    double? deliveryLongitude,
    List<OrderItem>? items,
    String? driverId,
    String? driverPhone,
    DateTime? estimatedDeliveryAt,
    DateTime? deliveredAt,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) {
    return Order(
      id: id ?? this.id,
      customerId: customerId ?? this.customerId,
      storeId: storeId ?? this.storeId,
      storeName: storeName ?? this.storeName,
      status: status ?? this.status,
      paymentStatus: paymentStatus ?? this.paymentStatus,
      subtotal: subtotal ?? this.subtotal,
      discount: discount ?? this.discount,
      deliveryFee: deliveryFee ?? this.deliveryFee,
      platformFee: platformFee ?? this.platformFee,
      total: total ?? this.total,
      deliveryAddress: deliveryAddress ?? this.deliveryAddress,
      deliveryLatitude: deliveryLatitude ?? this.deliveryLatitude,
      deliveryLongitude: deliveryLongitude ?? this.deliveryLongitude,
      items: items ?? this.items,
      driverId: driverId ?? this.driverId,
      driverPhone: driverPhone ?? this.driverPhone,
      estimatedDeliveryAt: estimatedDeliveryAt ?? this.estimatedDeliveryAt,
      deliveredAt: deliveredAt ?? this.deliveredAt,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }
}
