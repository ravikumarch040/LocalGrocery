import 'dart:async';

import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:models/models.dart' as models;

import 'api_providers.dart';

part 'cart_provider.g.dart';

/// Cart state provider
@riverpod
class Cart extends _$Cart {
  @override
  FutureOr<models.Cart?> build() async {
    final cartService = ref.read(cartServiceProvider);
    final response = await cartService.getCart();
    if (response.success) {
      return response.data;
    }
    return null;
  }

  /// Add a product to the cart (quantity defaults to 1)
  Future<void> addItem({
    required String productId,
    required String storeId,
    int quantity = 1,
  }) async {
    final previous = state;
    state = const AsyncValue.loading();

    final cartService = ref.read(cartServiceProvider);
    final response = await cartService.addItem(
      productId: productId,
      storeId: storeId,
      quantity: quantity,
    );

    if (response.success) {
      state = AsyncValue.data(response.data);
    } else {
      state = previous;
      throw Exception(response.message ?? 'Failed to add item to cart');
    }
  }

  /// Update cart item quantity
  Future<void> updateItem({required String itemId, required int quantity}) async {
    if (quantity < 1) {
      await removeItem(itemId);
      return;
    }
    final previous = state;
    state = const AsyncValue.loading();
    final cartService = ref.read(cartServiceProvider);
    final response = await cartService.updateItem(itemId: itemId, quantity: quantity);
    if (response.success) {
      state = AsyncValue.data(response.data);
    } else {
      state = previous;
      throw Exception(response.message ?? 'Failed to update quantity');
    }
  }

  /// Remove item from cart
  Future<void> removeItem(String itemId) async {
    final previous = state;
    state = const AsyncValue.loading();
    final cartService = ref.read(cartServiceProvider);
    final response = await cartService.removeItem(itemId);
    if (response.success) {
      state = AsyncValue.data(response.data);
    } else {
      state = previous;
      throw Exception(response.message ?? 'Failed to remove item');
    }
  }

  /// Apply coupon code
  Future<void> applyCoupon(String couponCode) async {
    final previous = state;
    state = const AsyncValue.loading();
    final cartService = ref.read(cartServiceProvider);
    final response = await cartService.applyCoupon(couponCode.trim());
    if (response.success) {
      state = AsyncValue.data(response.data);
    } else {
      state = previous;
      throw Exception(response.message ?? 'Failed to apply coupon');
    }
  }

  /// Remove applied coupon
  Future<void> removeCoupon() async {
    final previous = state;
    state = const AsyncValue.loading();
    final cartService = ref.read(cartServiceProvider);
    final response = await cartService.removeCoupon();
    if (response.success) {
      state = AsyncValue.data(response.data);
    } else {
      state = previous;
      throw Exception(response.message ?? 'Failed to remove coupon');
    }
  }

  /// Refresh cart from server
  Future<void> refresh() async {
    ref.invalidateSelf();
  }
}

