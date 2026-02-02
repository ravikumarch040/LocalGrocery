import 'package:json_annotation/json_annotation.dart';

part 'store.g.dart';

@JsonSerializable()
class Store {
  final String id;
  final String name;
  @JsonKey(name: 'image_url')
  final String? imageUrl;
  final String description;
  final double latitude;
  final double longitude;
  @JsonKey(name: 'delivery_radius_km')
  final double deliveryRadiusKm;
  @JsonKey(name: 'min_order_value')
  final double minOrderValue;
  final double rating;
  @JsonKey(name: 'total_reviews')
  final int totalReviews;
  @JsonKey(name: 'is_open')
  final bool isOpen;
  @JsonKey(name: 'kyc_status')
  final String kycStatus;
  @JsonKey(name: 'created_at')
  final DateTime? createdAt;

  const Store({
    required this.id,
    required this.name,
    this.imageUrl,
    required this.description,
    required this.latitude,
    required this.longitude,
    required this.deliveryRadiusKm,
    required this.minOrderValue,
    required this.rating,
    required this.totalReviews,
    required this.isOpen,
    required this.kycStatus,
    this.createdAt,
  });

  factory Store.fromJson(Map<String, dynamic> json) => _$StoreFromJson(json);
  Map<String, dynamic> toJson() => _$StoreToJson(this);
}
