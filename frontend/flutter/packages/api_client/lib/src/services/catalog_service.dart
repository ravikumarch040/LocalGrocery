import 'package:api_client/src/api_client.dart' as api;
import 'package:models/models.dart' as models;

/// Store product (product in a store's inventory: product + stock/price)
class StoreProduct {
  final String id;
  final String storeId;
  final String productId;
  final models.Product? product;
  final int stockQuantity;
  final double? storePrice;
  final bool isAvailable;

  StoreProduct({
    required this.id,
    required this.storeId,
    required this.productId,
    this.product,
    this.stockQuantity = 0,
    this.storePrice,
    this.isAvailable = true,
  });

  factory StoreProduct.fromJson(Map<String, dynamic> json) {
    models.Product? product;
    if (json['product'] != null) {
      product = models.Product.fromJson(json['product'] as Map<String, dynamic>);
    }
    final storePriceVal = json['store_price'];
    final double? storePrice = storePriceVal == null
        ? null
        : storePriceVal is num
            ? storePriceVal.toDouble()
            : double.tryParse(storePriceVal.toString());
    return StoreProduct(
      id: json['id'] as String,
      storeId: json['store_id'] as String,
      productId: json['product_id'] as String,
      product: product,
      stockQuantity: (json['stock_quantity'] as num?)?.toInt() ?? 0,
      storePrice: storePrice,
      isAvailable: json['is_available'] as bool? ?? true,
    );
  }
}

/// Catalog API service (paths under /api/v1)
class CatalogService {
  final api.ApiClient _apiClient;

  CatalogService(this._apiClient);

  static const String _prefix = '/api/v1';

  /// Search products (GET /api/v1/products/search/)
  Future<api.ApiResponse<List<models.Product>>> searchProducts({
    required String query,
    int page = 1,
    int pageSize = 20,
    String? categoryId,
    double? minPrice,
    double? maxPrice,
  }) async {
    return await _apiClient.get(
      '$_prefix/products/search/',
      queryParams: {
        'q': query,
        'page': page.toString(),
        'page_size': pageSize.toString(),
        if (categoryId != null) 'category_id': categoryId,
        if (minPrice != null) 'min_price': minPrice.toString(),
        if (maxPrice != null) 'max_price': maxPrice.toString(),
      },
      fromJson: (json) {
        final List<dynamic> products = (json['products'] as List?) ?? [];
        return products.map((p) => models.Product.fromJson(p as Map<String, dynamic>)).toList();
      },
    );
  }

  /// List products with filters (GET /api/v1/products/)
  Future<api.ApiResponse<List<models.Product>>> listProducts({
    String? categoryId,
    int page = 1,
    int pageSize = 20,
    double? minPrice,
    double? maxPrice,
  }) async {
    return await _apiClient.get(
      '$_prefix/products/',
      queryParams: {
        'page': page.toString(),
        'page_size': pageSize.toString(),
        if (categoryId != null) 'category_id': categoryId,
        if (minPrice != null) 'min_price': minPrice.toString(),
        if (maxPrice != null) 'max_price': maxPrice.toString(),
      },
      fromJson: (json) {
        final List<dynamic> products = (json['products'] as List?) ?? [];
        return products.map((p) => models.Product.fromJson(p as Map<String, dynamic>)).toList();
      },
    );
  }

  /// Get product details (GET /api/v1/products/{product_id})
  Future<api.ApiResponse<models.Product>> getProduct(String productId) async {
    return await _apiClient.get(
      '$_prefix/products/$productId',
      fromJson: (json) => models.Product.fromJson(json as Map<String, dynamic>),
    );
  }

  /// Create product (POST /api/v1/products/) - ProductCreate: name, category_id, base_price, description?, unit?, image_url?, is_active?
  Future<api.ApiResponse<models.Product>> createProduct({
    required String name,
    required String categoryId,
    required double basePrice,
    String? description,
    String? unit,
    String? imageUrl,
    bool isActive = true,
  }) async {
    return await _apiClient.post(
      '$_prefix/products/',
      body: {
        'name': name,
        'category_id': categoryId,
        'base_price': basePrice,
        if (description != null) 'description': description,
        if (unit != null) 'unit': unit,
        if (imageUrl != null) 'image_url': imageUrl,
        'is_active': isActive,
      },
      fromJson: (json) => models.Product.fromJson(json as Map<String, dynamic>),
    );
  }

  /// Update product (PUT /api/v1/products/{product_id})
  Future<api.ApiResponse<models.Product>> updateProduct({
    required String productId,
    String? name,
    String? categoryId,
    double? basePrice,
    String? description,
    String? unit,
    String? imageUrl,
    bool? isActive,
  }) async {
    return await _apiClient.put(
      '$_prefix/products/$productId',
      body: {
        if (name != null) 'name': name,
        if (categoryId != null) 'category_id': categoryId,
        if (basePrice != null) 'base_price': basePrice,
        if (description != null) 'description': description,
        if (unit != null) 'unit': unit,
        if (imageUrl != null) 'image_url': imageUrl,
        if (isActive != null) 'is_active': isActive,
      },
      fromJson: (json) => models.Product.fromJson(json as Map<String, dynamic>),
    );
  }

  /// Get categories (GET /api/v1/categories/)
  Future<api.ApiResponse<List<models.Category>>> getCategories() async {
    return await _apiClient.get(
      '$_prefix/categories/',
      fromJson: (json) {
        if (json is! List) {
          throw Exception('Expected List but got ${json.runtimeType}');
        }
        final List<dynamic> categories = json;
        return categories.map((c) => models.Category.fromJson(c as Map<String, dynamic>)).toList();
      },
    );
  }

  /// Get nearby stores (if backend supports)
  Future<api.ApiResponse<List<models.Store>>> getNearbyStores({
    required double latitude,
    required double longitude,
    double radius = 5.0,
  }) async {
    return await _apiClient.get(
      '$_prefix/stores/nearby',
      queryParams: {
        'latitude': latitude.toString(),
        'longitude': longitude.toString(),
        'radius': radius.toString(),
      },
      fromJson: (json) {
        final list = json is List ? json : (json['stores'] as List? ?? []);
        return list.map((s) => models.Store.fromJson(s as Map<String, dynamic>)).toList();
      },
    );
  }

  /// Get store details (if backend supports GET /api/v1/stores/{store_id})
  Future<api.ApiResponse<models.Store>> getStore(String storeId) async {
    return await _apiClient.get(
      '$_prefix/stores/$storeId',
      fromJson: (json) => models.Store.fromJson(json as Map<String, dynamic>),
    );
  }

  /// List store products (GET /api/v1/store-products/store/{store_id}) - returns array of StoreProductResponse
  Future<api.ApiResponse<List<StoreProduct>>> listStoreProducts({
    required String storeId,
    int page = 1,
    int pageSize = 100,
    String? categoryId,
    bool? isAvailable,
  }) async {
    return await _apiClient.get(
      '$_prefix/store-products/store/$storeId',
      queryParams: {
        'page': page.toString(),
        'page_size': pageSize.toString(),
        if (categoryId != null) 'category_id': categoryId,
        if (isAvailable != null) 'is_available': isAvailable.toString(),
      },
      fromJson: (json) {
        final list = json is List ? json : (json['products'] as List? ?? []);
        return list.map((e) => StoreProduct.fromJson(e as Map<String, dynamic>)).toList();
      },
    );
  }

  /// Get store product (GET /api/v1/store-products/{store_product_id})
  Future<api.ApiResponse<StoreProduct>> getStoreProduct(String storeProductId) async {
    return await _apiClient.get(
      '$_prefix/store-products/$storeProductId',
      fromJson: (json) => StoreProduct.fromJson(json as Map<String, dynamic>),
    );
  }

  /// Add product to store (POST /api/v1/store-products/) - StoreProductCreate: store_id, product_id, stock_quantity?, store_price?, is_available?
  Future<api.ApiResponse<StoreProduct>> addProductToStore({
    required String storeId,
    required String productId,
    int stockQuantity = 0,
    double? storePrice,
    bool isAvailable = true,
  }) async {
    return await _apiClient.post(
      '$_prefix/store-products/',
      body: {
        'store_id': storeId,
        'product_id': productId,
        'stock_quantity': stockQuantity,
        if (storePrice != null) 'store_price': storePrice,
        'is_available': isAvailable,
      },
      fromJson: (json) => StoreProduct.fromJson(json as Map<String, dynamic>),
    );
  }

  /// Update store product (PUT /api/v1/store-products/{store_product_id}) - stock, price, availability
  Future<api.ApiResponse<StoreProduct>> updateStoreProduct({
    required String storeProductId,
    int? stockQuantity,
    double? storePrice,
    bool? isAvailable,
  }) async {
    return await _apiClient.put(
      '$_prefix/store-products/$storeProductId',
      body: {
        if (stockQuantity != null) 'stock_quantity': stockQuantity,
        if (storePrice != null) 'store_price': storePrice,
        if (isAvailable != null) 'is_available': isAvailable,
      },
      fromJson: (json) => StoreProduct.fromJson(json as Map<String, dynamic>),
    );
  }

  /// Legacy: get store products as Product list (uses listStoreProducts and maps to product)
  Future<api.ApiResponse<List<models.Product>>> getStoreProducts({
    required String storeId,
    int page = 1,
    int pageSize = 20,
    String? category,
  }) async {
    final res = await listStoreProducts(
      storeId: storeId,
      page: page,
      pageSize: pageSize,
      categoryId: category,
    );
    if (!res.success || res.data == null) {
      return api.ApiResponse.error(message: res.message ?? 'Failed');
    }
    final products = res.data!
        .where((sp) => sp.product != null)
        .map((sp) => sp.product!)
        .toList();
    return api.ApiResponse.success(data: products, statusCode: res.statusCode);
  }
}
