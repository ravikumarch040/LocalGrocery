import 'package:api_client/src/api_client.dart' as api;
import 'package:models/models.dart' as models;

/// Catalog API service
class CatalogService {
  final api.ApiClient _apiClient;

  CatalogService(this._apiClient);

  /// Search products
  Future<api.ApiResponse<List<models.Product>>> searchProducts({
    required String query,
    int page = 1,
    int pageSize = 20,
    String? categoryId,
    double? minPrice,
    double? maxPrice,
  }) async {
    return await _apiClient.get(
      '/api/v1/products/search',
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

  /// List products with filters
  Future<api.ApiResponse<List<models.Product>>> listProducts({
    String? categoryId,
    int page = 1,
    int pageSize = 20,
    double? minPrice,
    double? maxPrice,
  }) async {
    return await _apiClient.get(
      '/api/v1/products',
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

  /// Get product details
  Future<api.ApiResponse<models.Product>> getProduct(String productId) async {
    return await _apiClient.get(
      '/api/v1/products/$productId',
      fromJson: (json) => models.Product.fromJson(json),
    );
  }

  /// Get categories
  Future<api.ApiResponse<List<models.Category>>> getCategories() async {
    return await _apiClient.get(
      '/api/v1/categories',
      fromJson: (json) {
        // Backend returns a direct List
        if (json is! List) {
          throw Exception('Expected List but got ${json.runtimeType}');
        }
        final List<dynamic> categories = json;
        return categories.map((c) => models.Category.fromJson(c as Map<String, dynamic>)).toList();
      },
    );
  }

  /// Get nearby stores
  Future<api.ApiResponse<List<models.Store>>> getNearbyStores({
    required double latitude,
    required double longitude,
    double radius = 5.0,
  }) async {
    return await _apiClient.get(
      '/catalog/stores/nearby',
      queryParams: {
        'latitude': latitude.toString(),
        'longitude': longitude.toString(),
        'radius': radius.toString(),
      },
      fromJson: (json) {
        final stores = json['stores'] as List;
        return stores.map((s) => models.Store.fromJson(s)).toList();
      },
    );
  }

  /// Get store details
  Future<api.ApiResponse<models.Store>> getStore(String storeId) async {
    return await _apiClient.get(
      '/catalog/stores/$storeId',
      fromJson: (json) => models.Store.fromJson(json),
    );
  }

  /// Get store products
  Future<api.ApiResponse<List<models.Product>>> getStoreProducts({
    required String storeId,
    int page = 1,
    int pageSize = 20,
    String? category,
  }) async {
    return await _apiClient.get(
      '/catalog/stores/$storeId/products',
      queryParams: {
        'page': page.toString(),
        'page_size': pageSize.toString(),
        if (category != null) 'category': category,
      },
      fromJson: (json) {
        final products = json['products'] as List;
        return products.map((p) => models.Product.fromJson(p)).toList();
      },
    );
  }
}
