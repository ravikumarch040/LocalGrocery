import 'package:api_client/src/api_client.dart' as api;
import 'package:models/models.dart' as models;

/// Cart API service
class CartService {
  final api.ApiClient _apiClient;

  CartService(this._apiClient);

  /// Get user's cart
  Future<api.ApiResponse<models.Cart>> getCart() async {
    return await _apiClient.get(
      '/cart',
      fromJson: (json) => models.Cart.fromJson(json),
    );
  }

  /// Add item to cart
  Future<api.ApiResponse<models.Cart>> addItem({
    required String productId,
    required String storeId,
    required int quantity,
  }) async {
    return await _apiClient.post(
      '/cart/items',
      body: {
        'product_id': productId,
        'store_id': storeId,
        'quantity': quantity,
      },
      fromJson: (json) => models.Cart.fromJson(json),
    );
  }

  /// Update cart item quantity
  Future<api.ApiResponse<models.Cart>> updateItem({
    required String itemId,
    required int quantity,
  }) async {
    return await _apiClient.put(
      '/cart/items/$itemId',
      body: {'quantity': quantity},
      fromJson: (json) => models.Cart.fromJson(json),
    );
  }

  /// Remove item from cart
  Future<api.ApiResponse<models.Cart>> removeItem(String itemId) async {
    return await _apiClient.delete(
      '/cart/items/$itemId',
      fromJson: (json) => models.Cart.fromJson(json),
    );
  }

  /// Clear entire cart
  Future<api.ApiResponse<void>> clearCart() async {
    return await _apiClient.delete('/cart');
  }

  /// Apply coupon code
  Future<api.ApiResponse<models.Cart>> applyCoupon(String couponCode) async {
    return await _apiClient.post(
      '/cart/coupon',
      body: {'coupon_code': couponCode},
      fromJson: (json) => models.Cart.fromJson(json),
    );
  }

  /// Remove coupon
  Future<api.ApiResponse<models.Cart>> removeCoupon() async {
    return await _apiClient.delete(
      '/cart/coupon',
      fromJson: (json) => models.Cart.fromJson(json),
    );
  }
}
