import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:api_client/api_client.dart';
import 'package:core/core.dart';

final apiClientProvider = Provider<ApiClient>((ref) {
  final base = AppConfig.apiGatewayUrl.isNotEmpty
      ? AppConfig.apiGatewayUrl
      : AppConfig.authServiceUrl.isNotEmpty
          ? AppConfig.authServiceUrl
          : 'http://localhost:8001';
  return ApiClient(baseUrl: base);
});

final authServiceProvider = Provider<AuthService>((ref) {
  final base = AppConfig.authServiceUrl.isNotEmpty
      ? AppConfig.authServiceUrl
      : AppConfig.apiGatewayUrl.isNotEmpty
          ? AppConfig.apiGatewayUrl
          : 'http://localhost:8001';
  final client = ApiClient(baseUrl: base);
  return AuthService(client);
});

final catalogServiceProvider = Provider<CatalogService>((ref) {
  final base = AppConfig.catalogServiceUrl.isNotEmpty
      ? AppConfig.catalogServiceUrl
      : 'http://localhost:8002';
  final client = ApiClient(baseUrl: base);
  return CatalogService(client);
});

final orderServiceProvider = Provider<OrderService>((ref) {
  final base = AppConfig.orderServiceUrl.isNotEmpty
      ? AppConfig.orderServiceUrl
      : 'http://localhost:8003';
  final client = ApiClient(baseUrl: base);
  return OrderService(client);
});
