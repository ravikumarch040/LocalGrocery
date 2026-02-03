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

/// Recent orders for analytics (no status filter, larger page size).
final retailerOrdersForAnalyticsProvider =
    FutureProvider.autoDispose<List<Order>>((ref) async {
  final store = await ref.watch(retailerStoreProvider.future);
  if (store == null) return [];
  final orderService = ref.read(orderServiceProvider);
  final res = await orderService.getOrders(
    storeId: store.id,
    status: null,
    pageSize: 100,
  );
  if (!res.success || res.data == null) return [];
  return res.data!;
});

/// Analytics data derived from orders: today stats, 7-day series, top products.
class RetailerAnalytics {
  final int todayOrderCount;
  final double todayRevenue;
  final List<({int dayOffset, double revenue})> last7Days;
  final List<({String name, int quantity, double revenue})> topProducts;

  RetailerAnalytics({
    required this.todayOrderCount,
    required this.todayRevenue,
    required this.last7Days,
    required this.topProducts,
  });
}

final retailerAnalyticsProvider =
    FutureProvider.autoDispose<RetailerAnalytics>((ref) async {
  final orders = await ref.watch(retailerOrdersForAnalyticsProvider.future);
  final now = DateTime.now();
  final todayStart = DateTime(now.year, now.month, now.day);

  int todayOrderCount = 0;
  double todayRevenue = 0;
  final dayRevenue = List.filled(7, 0.0);
  final Map<String, ({int qty, double rev})> productMap = {};

  for (final o in orders) {
    final created = o.createdAt;
    if (created == null) continue;
    final isToday = !created.isBefore(todayStart) && created.isBefore(todayStart.add(const Duration(days: 1)));
    if (isToday) {
      todayOrderCount++;
      todayRevenue += o.total;
    }
    final daysAgo = now.difference(DateTime(created.year, created.month, created.day)).inDays;
    if (daysAgo >= 0 && daysAgo < 7) {
      dayRevenue[6 - daysAgo] += o.total;
    }
    for (final item in o.items) {
      final name = item.name;
      final existing = productMap[name];
      if (existing == null) {
        productMap[name] = (qty: item.quantity, rev: item.subtotal);
      } else {
        productMap[name] = (qty: existing.qty + item.quantity, rev: existing.rev + item.subtotal);
      }
    }
  }

  final last7Days = List.generate(7, (i) {
    final d = now.subtract(Duration(days: 6 - i));
    return (dayOffset: i, revenue: dayRevenue[i]);
  });

  final topProducts = productMap.entries
      .map((e) => (name: e.key, quantity: e.value.qty, revenue: e.value.rev))
      .toList()
    ..sort((a, b) => b.revenue.compareTo(a.revenue));
  final top5 = topProducts.take(5).toList();

  return RetailerAnalytics(
    todayOrderCount: todayOrderCount,
    todayRevenue: todayRevenue,
    last7Days: last7Days,
    topProducts: top5,
  );
});
