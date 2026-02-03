import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:models/models.dart' as models;
import 'package:core/core.dart';

import '../../providers/order_provider.dart';

const _activeStatuses = {'placed', 'confirmed', 'packed', 'out_for_delivery', 'pending'};
const _pastStatuses = {'delivered', 'cancelled'};

class OrdersScreen extends ConsumerStatefulWidget {
  const OrdersScreen({super.key});

  @override
  ConsumerState<OrdersScreen> createState() => _OrdersScreenState();
}

class _OrdersScreenState extends ConsumerState<OrdersScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final ordersAsync = ref.watch(ordersListProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('My Orders'),
        backgroundColor: Colors.green,
        foregroundColor: Colors.white,
        bottom: TabBar(
          controller: _tabController,
          labelColor: Colors.white,
          unselectedLabelColor: Colors.white70,
          tabs: const [
            Tab(text: 'Active'),
            Tab(text: 'Past'),
          ],
        ),
      ),
      body: ordersAsync.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (err, _) => AsyncErrorView(
          error: err,
          onRetry: () => ref.invalidate(ordersListProvider),
        ),
        data: (allOrders) {
          final active = allOrders
              .where((o) => _activeStatuses.contains(o.status.toLowerCase()))
              .toList();
          final past = allOrders
              .where((o) => _pastStatuses.contains(o.status.toLowerCase()))
              .toList();
          return TabBarView(
            controller: _tabController,
            children: [
              _OrderList(orders: active),
              _OrderList(orders: past),
            ],
          );
        },
      ),
    );
  }
}

class _OrderList extends StatelessWidget {
  final List<models.Order> orders;

  const _OrderList({required this.orders});

  @override
  Widget build(BuildContext context) {
    if (orders.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.receipt_long_outlined, size: 64, color: Colors.grey[400]),
            const SizedBox(height: 16),
            Text(
              'No orders here',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    color: Colors.grey[600],
                  ),
            ),
          ],
        ),
      );
    }
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: orders.length,
      itemBuilder: (context, index) {
        final order = orders[index];
        return _OrderCard(order: order);
      },
    );
  }
}

class _OrderCard extends StatelessWidget {
  final models.Order order;

  const _OrderCard({required this.order});

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: InkWell(
        onTap: () => context.push('/orders/${order.id}'),
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    order.storeName.isNotEmpty ? order.storeName : 'Order',
                    style: const TextStyle(
                      fontWeight: FontWeight.w600,
                      fontSize: 16,
                    ),
                  ),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: _statusColor(order.status).withOpacity(0.2),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Text(
                      _formatStatus(order.status),
                      style: TextStyle(
                        fontSize: 12,
                        fontWeight: FontWeight.w600,
                        color: _statusColor(order.status),
                      ),
                    ),
                  ),
                ],
              ),
              if (order.createdAt != null) ...[
                const SizedBox(height: 4),
                Text(
                  _formatDate(order.createdAt!),
                  style: TextStyle(fontSize: 12, color: Colors.grey[600]),
                ),
              ],
              const SizedBox(height: 8),
              Text(
                '${order.items.length} item(s) • ₹${order.total.toStringAsFixed(0)}',
                style: TextStyle(fontSize: 13, color: Colors.grey[700]),
              ),
              const SizedBox(height: 12),
              Row(
                mainAxisAlignment: MainAxisAlignment.end,
                children: [
                  TextButton(
                    onPressed: () => context.push('/orders/${order.id}'),
                    child: const Text('View details'),
                  ),
                  if (_pastStatuses.contains(order.status.toLowerCase()) &&
                      order.status.toLowerCase() == 'delivered')
                    TextButton(
                      onPressed: () => context.push('/orders/${order.id}/rate'),
                      child: const Text('Rate'),
                    ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Color _statusColor(String status) {
    switch (status.toLowerCase()) {
      case 'delivered':
        return Colors.green;
      case 'cancelled':
        return Colors.red;
      case 'out_for_delivery':
        return Colors.blue;
      default:
        return Colors.orange;
    }
  }

  String _formatStatus(String s) {
    return s.replaceAll('_', ' ').split(' ').map((e) => e.isEmpty ? e : '${e[0].toUpperCase()}${e.substring(1).toLowerCase()}').join(' ');
  }

  String _formatDate(DateTime d) {
    return '${d.day}/${d.month}/${d.year} ${d.hour.toString().padLeft(2, '0')}:${d.minute.toString().padLeft(2, '0')}';
  }
}
