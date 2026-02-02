import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:models/models.dart' as models;

import 'api_providers.dart';

part 'order_provider.g.dart';

/// All orders (filter Active/Past in UI by status)
@riverpod
Future<List<models.Order>> ordersList(OrdersListRef ref) async {
  final orderService = ref.watch(orderServiceProvider);
  final response = await orderService.getOrders(page: 1, pageSize: 50);
  if (response.success && response.data != null) return response.data!;
  throw Exception(response.message ?? 'Failed to load orders');
}

/// Single order details
@riverpod
Future<models.Order> orderDetail(OrderDetailRef ref, String orderId) async {
  final orderService = ref.watch(orderServiceProvider);
  final response = await orderService.getOrder(orderId);
  if (response.success && response.data != null) return response.data!;
  throw Exception(response.message ?? 'Failed to load order');
}
