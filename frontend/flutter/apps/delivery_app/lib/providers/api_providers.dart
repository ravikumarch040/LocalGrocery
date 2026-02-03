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
      : 'http://localhost:8001';
  return AuthService(ApiClient(baseUrl: base));
});

final deliveryServiceProvider = Provider<DeliveryService>((ref) {
  final base = AppConfig.deliveryServiceUrl.isNotEmpty
      ? AppConfig.deliveryServiceUrl
      : 'http://localhost:8005';
  return DeliveryService(ApiClient(baseUrl: base));
});

final orderServiceProvider = Provider<OrderService>((ref) {
  final base = AppConfig.orderServiceUrl.isNotEmpty
      ? AppConfig.orderServiceUrl
      : 'http://localhost:8003';
  return OrderService(ApiClient(baseUrl: base));
});
