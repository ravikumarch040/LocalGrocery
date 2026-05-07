import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:core/core.dart';
import '../../providers/order_provider.dart';

class OrdersScreen extends ConsumerStatefulWidget {
  const OrdersScreen({super.key});

  @override
  ConsumerState<OrdersScreen> createState() => _OrdersScreenState();
}

class _OrdersScreenState extends ConsumerState<OrdersScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;

  static const List<Map<String, String?>> _tabs = [
    {'label': 'New', 'status': 'PLACED'},
    {'label': 'Confirmed', 'status': 'CONFIRMED'},
    {'label': 'Packed', 'status': 'PACKED'},
    {'label': 'Out for delivery', 'status': 'OUT_FOR_DELIVERY'},
    {'label': 'Completed', 'status': 'DELIVERED'},
  ];

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: _tabs.length, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Orders'),
        bottom: TabBar(
          controller: _tabController,
          isScrollable: true,
          tabs: _tabs.map((t) => Tab(text: t['label'])).toList(),
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: _tabs
            .map((t) => _OrdersList(status: t['status']))
            .toList(),
      ),
    );
  }
}

class _OrdersList extends ConsumerWidget {
  final String? status;

  const _OrdersList({this.status});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final ordersAsync = ref.watch(retailerOrdersProvider(status));

    return ordersAsync.when(
      data: (orders) {
        if (orders.isEmpty) {
          return Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(Icons.receipt_long_outlined, size: 64, color: Colors.grey.shade400),
                const SizedBox(height: 16),
                Text(
                  'No orders',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        color: Colors.grey.shade600,
                      ),
                ),
              ],
            ),
          );
        }
        return RefreshIndicator(
          onRefresh: () async => ref.invalidate(retailerOrdersProvider),
          child: ListView.builder(
            padding: const EdgeInsets.all(16),
            itemCount: orders.length,
            itemBuilder: (context, index) {
              final order = orders[index];
              return Card(
                margin: const EdgeInsets.only(bottom: 12),
                child: ListTile(
                  title: Text('Order #${order.id.substring(0, 8)}'),
                  subtitle: Text(
                    '${order.items.fold<int>(0, (s, i) => s + i.quantity)} items · ₹${order.total.toStringAsFixed(0)}',
                  ),
                  trailing: const Icon(Icons.chevron_right),
                  onTap: () => context.push('/orders/${order.id}'),
                ),
              );
            },
          ),
        );
      },
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (e, _) => AsyncErrorView(
        error: e,
        onRetry: () => ref.invalidate(retailerOrdersProvider(status)),
      ),
    );
  }
}
