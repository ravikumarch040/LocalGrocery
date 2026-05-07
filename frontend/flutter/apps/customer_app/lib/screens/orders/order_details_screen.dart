import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:models/models.dart' as models;
import 'package:url_launcher/url_launcher.dart';
import 'package:core/core.dart';

import '../../providers/order_provider.dart';
import '../../providers/api_providers.dart';

class OrderDetailsScreen extends ConsumerWidget {
  final String orderId;

  const OrderDetailsScreen({super.key, required this.orderId});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final orderAsync = ref.watch(orderDetailProvider(orderId));

    return Scaffold(
      appBar: AppBar(
        title: const Text('Order Details'),
        backgroundColor: Colors.green,
        foregroundColor: Colors.white,
        actions: [
          IconButton(
            icon: const Icon(Icons.help_outline),
            onPressed: () {
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('Help & support coming soon')),
              );
            },
          ),
        ],
      ),
      body: orderAsync.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (err, _) => AsyncErrorView(
          error: err,
          onRetry: () => ref.invalidate(orderDetailProvider(orderId)),
        ),
        data: (order) => SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _StatusChip(status: order.status),
              const SizedBox(height: 16),
              Text(
                order.storeName.isNotEmpty ? order.storeName : 'Order',
                style: Theme.of(context).textTheme.titleLarge?.copyWith(
                      fontWeight: FontWeight.w600,
                    ),
              ),
              if (order.createdAt != null)
                Text(
                  'Placed on ${_formatDate(order.createdAt!)}',
                  style: TextStyle(fontSize: 12, color: Colors.grey[600]),
                ),
              const SizedBox(height: 16),
              const Text('Items', style: TextStyle(fontWeight: FontWeight.w600)),
              const SizedBox(height: 8),
              ...order.items.map(
                (item) => Padding(
                  padding: const EdgeInsets.only(bottom: 8),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Expanded(
                        child: Text(
                          '${item.name} × ${item.quantity}',
                          style: const TextStyle(fontSize: 14),
                        ),
                      ),
                      Text(
                        '₹${item.subtotal.toStringAsFixed(0)}',
                        style: const TextStyle(
                          fontWeight: FontWeight.w600,
                          color: Colors.green,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
              const Divider(height: 24),
              _PriceRow(label: 'Subtotal', value: order.subtotal),
              if (order.discount > 0) _PriceRow(label: 'Discount', value: -order.discount, valueColor: Colors.green),
              if (order.deliveryFee > 0) _PriceRow(label: 'Delivery', value: order.deliveryFee),
              if (order.platformFee > 0) _PriceRow(label: 'Platform fee', value: order.platformFee),
              _PriceRow(label: 'Total', value: order.total, isTotal: true),
              const SizedBox(height: 16),
              const Text('Delivery address', style: TextStyle(fontWeight: FontWeight.w600)),
              const SizedBox(height: 4),
              Text(order.deliveryAddress, style: TextStyle(fontSize: 14, color: Colors.grey[700])),
              const SizedBox(height: 24),
              Row(
                children: [
                  if (_canTrack(order.status))
                    Expanded(
                      child: FilledButton.icon(
                        onPressed: () => context.push('/orders/$orderId/track'),
                        icon: const Icon(Icons.location_on),
                        label: const Text('Track order'),
                        style: FilledButton.styleFrom(backgroundColor: Colors.green),
                      ),
                    ),
                  if (_canTrack(order.status)) const SizedBox(width: 12),
                  if (_canCancel(order.status))
                    Expanded(
                      child: OutlinedButton.icon(
                        onPressed: () => _cancelOrder(context, ref, orderId),
                        icon: const Icon(Icons.cancel_outlined),
                        label: const Text('Cancel order'),
                      ),
                    ),
                  if (order.driverPhone != null && order.driverPhone!.isNotEmpty) ...[
                    const SizedBox(width: 12),
                    IconButton(
                      onPressed: () => _launchPhone(order.driverPhone!),
                      icon: const Icon(Icons.phone),
                      style: IconButton.styleFrom(
                        backgroundColor: Colors.green[100],
                        foregroundColor: Colors.green,
                      ),
                    ),
                  ],
                ],
              ),
              if (order.status.toLowerCase() == 'delivered') ...[
                const SizedBox(height: 12),
                SizedBox(
                  width: double.infinity,
                  child: OutlinedButton.icon(
                    onPressed: () => context.push('/orders/$orderId/rate'),
                    icon: const Icon(Icons.star_outline),
                    label: const Text('Rate this order'),
                  ),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  bool _canTrack(String status) {
    final s = status.toLowerCase();
    return s == 'confirmed' || s == 'packed' || s == 'out_for_delivery';
  }

  bool _canCancel(String status) {
    final s = status.toLowerCase();
    return s == 'placed' || s == 'pending';
  }

  String _formatDate(DateTime d) {
    return '${d.day}/${d.month}/${d.year} ${d.hour.toString().padLeft(2, '0')}:${d.minute.toString().padLeft(2, '0')}';
  }

  Future<void> _launchPhone(String phone) async {
    final uri = Uri(scheme: 'tel', path: phone.trim());
    if (await canLaunchUrl(uri)) {
      await launchUrl(uri);
    }
  }

  Future<void> _cancelOrder(BuildContext context, WidgetRef ref, String id) async {
    final ok = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Cancel order?'),
        content: const Text('This action cannot be undone.'),
        actions: [
          TextButton(onPressed: () => Navigator.of(ctx).pop(false), child: const Text('No')),
          TextButton(onPressed: () => Navigator.of(ctx).pop(true), child: const Text('Yes, cancel')),
        ],
      ),
    );
    if (ok != true || !context.mounted) return;
    try {
      final orderService = ref.read(orderServiceProvider);
      final response = await orderService.cancelOrder(orderId: id);
      if (response.success && context.mounted) {
        ref.invalidate(orderDetailProvider(id));
        ref.invalidate(ordersListProvider);
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Order cancelled')));
        context.pop();
      } else if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(response.message ?? 'Failed to cancel')),
        );
      }
    } catch (e) {
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Error: $e')));
      }
    }
  }
}

class _StatusChip extends StatelessWidget {
  final String status;

  const _StatusChip({required this.status});

  @override
  Widget build(BuildContext context) {
    Color color;
    switch (status.toLowerCase()) {
      case 'delivered':
        color = Colors.green;
        break;
      case 'cancelled':
        color = Colors.red;
        break;
      case 'out_for_delivery':
        color = Colors.blue;
        break;
      default:
        color = Colors.orange;
    }
    final label = status.replaceAll('_', ' ').split(' ').map((e) => e.isEmpty ? e : '${e[0].toUpperCase()}${e.substring(1).toLowerCase()}').join(' ');
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        color: color.withOpacity(0.2),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Text(label, style: TextStyle(fontWeight: FontWeight.w600, color: color)),
    );
  }
}

class _PriceRow extends StatelessWidget {
  final String label;
  final double value;
  final bool isTotal;
  final Color? valueColor;

  const _PriceRow({required this.label, required this.value, this.isTotal = false, this.valueColor});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: TextStyle(fontWeight: isTotal ? FontWeight.bold : FontWeight.w500)),
          Text(
            '₹${value.toStringAsFixed(0)}',
            style: TextStyle(
              fontWeight: isTotal ? FontWeight.bold : FontWeight.w500,
              color: valueColor ?? (isTotal ? Colors.green : null),
            ),
          ),
        ],
      ),
    );
  }
}
