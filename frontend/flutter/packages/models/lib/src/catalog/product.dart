import 'package:json_annotation/json_annotation.dart';

part 'product.g.dart';

@JsonSerializable()
class Product {
  final String id;
  final String name;
  final String? description;
  @JsonKey(name: 'image_url')
  final String? imageUrl;
  @JsonKey(name: 'category_id')
  final String categoryId;
  @JsonKey(name: 'base_price')
  final double basePrice;
  final String? unit;
  final dynamic variants;
  final bool isActive;
  @JsonKey(name: 'created_at')
  final DateTime? createdAt;
  @JsonKey(name: 'updated_at')
  final DateTime? updatedAt;

  // Computed properties for convenience
  double get price => basePrice;
  double get mrp => basePrice;
  int get stockQty => 0; // Will be fetched from store_products
  bool get inStock => isActive;

  const Product({
    required this.id,
    required this.name,
    this.description,
    this.imageUrl,
    required this.categoryId,
    required this.basePrice,
    this.unit,
    this.variants,
    this.isActive = true,
    this.createdAt,
    this.updatedAt,
  });

  factory Product.fromJson(Map<String, dynamic> json) {
    // Handle base_price as either string or number
    final basePriceValue = json['base_price'];
    final double parsedPrice;
    if (basePriceValue is String) {
      parsedPrice = double.parse(basePriceValue);
    } else if (basePriceValue is num) {
      parsedPrice = basePriceValue.toDouble();
    } else {
      parsedPrice = 0.0;
    }

    return Product(
      id: json['id'] as String,
      name: json['name'] as String,
      description: json['description'] as String?,
      imageUrl: json['image_url'] as String?,
      categoryId: json['category_id'] as String,
      basePrice: parsedPrice,
      unit: json['unit'] as String?,
      variants: json['variants'],
      isActive: json['is_active'] as bool? ?? true,
      createdAt: json['created_at'] != null ? DateTime.parse(json['created_at'] as String) : null,
      updatedAt: json['updated_at'] != null ? DateTime.parse(json['updated_at'] as String) : null,
    );
  }

  Map<String, dynamic> toJson() => _$ProductToJson(this);

  Product copyWith({
    String? id,
    String? name,
    String? description,
    String? imageUrl,
    String? categoryId,
    double? basePrice,
    String? unit,
    dynamic variants,
    bool? isActive,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) {
    return Product(
      id: id ?? this.id,
      name: name ?? this.name,
      description: description ?? this.description,
      imageUrl: imageUrl ?? this.imageUrl,
      categoryId: categoryId ?? this.categoryId,
      basePrice: basePrice ?? this.basePrice,
      unit: unit ?? this.unit,
      variants: variants ?? this.variants,
      isActive: isActive ?? this.isActive,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }
}
