import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:models/models.dart';
import 'package:core/core.dart';
import '../../providers/api_providers.dart';
import '../../providers/order_provider.dart';

final _orderDetailProvider =
    FutureProvider.autoDispose.family<Order?, String>((ref, orderId) async {
  final orderService = ref.read(orderServiceProvider);
  final res = await orderService.getOrder(orderId);
  if (res.success && res.data != null) return res.data;
  throw Exception(res.message ?? 'Order not found');
});

class OrderDetailsScreen extends ConsumerWidget {
  final String orderId;

  const OrderDetailsScreen({super.key, required this.orderId});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final orderAsync = ref.watch(_orderDetailProvider(orderId));

    return Scaffold(
      appBar: AppBar(
        title: Text('Order #${orderId.substring(0, 8)}'),
      ),
      body: orderAsync.when(
        data: (order) {
          if (order == null) {
            return const Center(child: Text('Order not found'));
          }
          return SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Card(
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Text(
                              order.status,
                              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                                    color: Colors.amber.shade700,
                                    fontWeight: FontWeight.bold,
                                  ),
                            ),
                            Chip(
                              label: Text(order.paymentStatus),
                              backgroundColor: order.paymentStatus == 'PAID'
                                  ? Colors.green.shade100
                                  : Colors.orange.shade100,
                            ),
                          ],
                        ),
                        const SizedBox(height: 12),
                        Text('Delivery: ${order.deliveryAddress}'),
                        const SizedBox(height: 8),
                        Text(
                          'Subtotal ₹${order.subtotal.toStringAsFixed(0)} · Total ₹${order.total.toStringAsFixed(0)}',
                          style: Theme.of(context).textTheme.bodySmall,
                        ),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 16),
                Text(
                  'Items',
                  style: Theme.of(context).textTheme.titleMedium,
                ),
                const SizedBox(height: 8),
                ...order.items.map(
                  (item) => ListTile(
                    leading: const Icon(Icons.inventory_2_outlined),
                    title: Text(item.name),
                    subtitle: Text('Qty: ${item.quantity}'),
                    trailing: Text(
                      '₹${(item.price * item.quantity).toStringAsFixed(0)}',
                    ),
                  ),
                ),
                const SizedBox(height: 24),
                if (order.status == 'PLACED') ...[
                  Row(
                    children: [
                      Expanded(
                        child: FilledButton.icon(
                          onPressed: () => _updateStatus(ref, context, 'CONFIRMED'),
                          icon: const Icon(Icons.check),
                          label: const Text('Accept'),
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: OutlinedButton.icon(
                          onPressed: () => _updateStatus(ref, context, 'CANCELLED'),
                          icon: const Icon(Icons.close),
                          label: const Text('Reject'),
                        ),
                      ),
                    ],
                  ),
                ] else if (order.status == 'CONFIRMED') ...[
                  FilledButton.icon(
                    onPressed: () => _updateStatus(ref, context, 'PACKED'),
                    icon: const Icon(Icons.inventory),
                    label: const Text('Mark as packed'),
                  ),
                ] else if (order.status == 'PACKED') ...[
                  FilledButton.icon(
                    onPressed: () => _updateStatus(ref, context, 'OUT_FOR_DELIVERY'),
                    icon: const Icon(Icons.local_shipping),
                    label: const Text('Out for delivery'),
                  ),
                ],
              ],
            ),
          );
        },
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => AsyncErrorView(
          error: e,
          onRetry: () => ref.invalidate(_orderDetailProvider(orderId)),
        ),
      ),
    );
  }

  Future<void> _updateStatus(WidgetRef ref, BuildContext context, String status) async {
    final orderService = ref.read(orderServiceProvider);
    final res = await orderService.updateOrderStatus(
      orderId: orderId,
      status: status,
    );
    if (!context.mounted) return;
    if (res.success) {
      ref.invalidate(_orderDetailProvider(orderId));
      ref.invalidate(retailerOrdersProvider);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Order ${status.toLowerCase()}')),
      );
      if (status == 'CANCELLED') {
        context.pop();
      }
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(res.message ?? 'Failed'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }
}
