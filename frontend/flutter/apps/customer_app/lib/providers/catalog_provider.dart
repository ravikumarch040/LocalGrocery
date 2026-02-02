import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:models/models.dart';
import 'api_providers.dart';

part 'catalog_provider.g.dart';

/// Fetch all categories
@riverpod
Future<List<Category>> categories(CategoriesRef ref) async {
  final catalogService = ref.watch(catalogServiceProvider);
  final response = await catalogService.getCategories();
  if (response.success && response.data != null) {
    return response.data!;
  }
  throw Exception(response.message ?? 'Failed to fetch categories');
}

/// Fetch featured products
@riverpod
Future<List<Product>> featuredProducts(FeaturedProductsRef ref) async {
  final catalogService = ref.watch(catalogServiceProvider);
  final response = await catalogService.listProducts(pageSize: 10);
  if (response.success && response.data != null) {
    return response.data!;
  }
  throw Exception(response.message ?? 'Failed to fetch featured products');
}

/// Search products by query
@riverpod
Future<List<Product>> searchProducts(SearchProductsRef ref, String query) async {
  if (query.isEmpty) {
    return [];
  }
  final catalogService = ref.watch(catalogServiceProvider);
  final response = await catalogService.searchProducts(query: query);
  if (response.success && response.data != null) {
    return response.data!;
  }
  throw Exception(response.message ?? 'Failed to search products');
}

/// Get products by category
@riverpod
Future<List<Product>> productsByCategory(
  ProductsByCategoryRef ref,
  String categoryId,
) async {
  final catalogService = ref.watch(catalogServiceProvider);
  final response = await catalogService.listProducts(categoryId: categoryId);
  if (response.success && response.data != null) {
    return response.data!;
  }
  throw Exception(response.message ?? 'Failed to fetch products');
}

/// Get product details
@riverpod
Future<Product> productDetail(ProductDetailRef ref, String productId) async {
  final catalogService = ref.watch(catalogServiceProvider);
  final response = await catalogService.getProduct(productId);
  if (response.success && response.data != null) {
    return response.data!;
  }
  throw Exception(response.message ?? 'Failed to fetch product');
}
