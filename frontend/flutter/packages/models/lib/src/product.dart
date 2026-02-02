/// Product model
class Product {
  final String id;
  final String name;
  final String? description;
  final String? imageUrl;
  final String category;
  final String? brand;
  final double price;
  final double? mrp;
  final String unit; // kg, g, L, ml, pack, etc.
  final int? stockQuantity;
  final bool inStock;
  final String? storeId;

  Product({
    required this.id,
    required this.name,
    this.description,
    this.imageUrl,
    required this.category,
    this.brand,
    required this.price,
    this.mrp,
    required this.unit,
    this.stockQuantity,
    required this.inStock,
    this.storeId,
  });

  factory Product.fromJson(Map<String, dynamic> json) {
    return Product(
      id: json['id'] as String,
      name: json['name'] as String,
      description: json['description'] as String?,
      imageUrl: json['image_url'] as String?,
      category: json['category'] as String,
      brand: json['brand'] as String?,
      price: (json['price'] as num).toDouble(),
      mrp: json['mrp'] != null ? (json['mrp'] as num).toDouble() : null,
      unit: json['unit'] as String,
      stockQuantity: json['stock_quantity'] as int?,
      inStock: json['in_stock'] as bool? ?? true,
      storeId: json['store_id'] as String?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'description': description,
      'image_url': imageUrl,
      'category': category,
      'brand': brand,
      'price': price,
      'mrp': mrp,
      'unit': unit,
      'stock_quantity': stockQuantity,
      'in_stock': inStock,
      'store_id': storeId,
    };
  }

  double? get discount {
    if (mrp != null && mrp! > price) {
      return ((mrp! - price) / mrp!) * 100;
    }
    return null;
  }
}

/// Category model
class Category {
  final String id;
  final String name;
  final String? imageUrl;
  final int productCount;

  Category({
    required this.id,
    required this.name,
    this.imageUrl,
    required this.productCount,
  });

  factory Category.fromJson(Map<String, dynamic> json) {
    return Category(
      id: json['id'] as String,
      name: json['name'] as String,
      imageUrl: json['image_url'] as String?,
      productCount: json['product_count'] as int? ?? 0,
    );
  }
}
