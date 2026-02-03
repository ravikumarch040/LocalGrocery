import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:models/models.dart';
import 'api_providers.dart';
import 'store_provider.dart';

/// Orders for the retailer's store. Pass status (e.g. PLACED, CONFIRMED) or null for all.
final retailerOrdersProvider =
    FutureProvider.autoDispose.family<List<Order>, String?>((ref, status) async {
  final store = await ref.watch(retailerStoreProvider.future);
  if (store == null) return [];
  final orderService = ref.read(orderServiceProvider);
  final res = await orderService.getOrders(
    storeId: store.id,
    status: status,
    pageSize: 50,
  );
  if (!res.success || res.data == null) return [];
  return res.data!;
});
