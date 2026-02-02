import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:api_client/api_client.dart';
import 'package:core/core.dart';

part 'api_providers.g.dart';

/// API Client provider
@riverpod
ApiClient apiClient(Ref ref) {
  final base = AppConfig.apiGatewayUrl.isNotEmpty
      ? AppConfig.apiGatewayUrl
      : AppConfig.authServiceUrl.isNotEmpty
          ? AppConfig.authServiceUrl
          : 'http://localhost:8001';
  return ApiClient(baseUrl: base);
}

/// Auth Service provider
@riverpod
AuthService authService(Ref ref) {
  final base = AppConfig.authServiceUrl.isNotEmpty
      ? AppConfig.authServiceUrl
      : AppConfig.apiGatewayUrl.isNotEmpty
          ? AppConfig.apiGatewayUrl
          : 'http://localhost:8001';
  final client = ApiClient(baseUrl: base);
  return AuthService(client);
}

/// Catalog Service provider
@riverpod
CatalogService catalogService(Ref ref) {
  final base = AppConfig.catalogServiceUrl.isNotEmpty
      ? AppConfig.catalogServiceUrl
      : 'http://localhost:8002';
  final client = ApiClient(baseUrl: base);
  return CatalogService(client);
}

/// Cart Service provider
@riverpod
CartService cartService(Ref ref) {
  final client = ApiClient(baseUrl: AppConfig.cartServiceUrl);
  return CartService(client);
}

/// Order Service provider
@riverpod
OrderService orderService(Ref ref) {
  final client = ApiClient(baseUrl: AppConfig.orderServiceUrl);
  return OrderService(client);
}
