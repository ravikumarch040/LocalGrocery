import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:core/core.dart';

import '../../providers/order_provider.dart';
import '../../providers/api_providers.dart';

class OrderTrackingScreen extends ConsumerWidget {
  final String orderId;

  const OrderTrackingScreen({super.key, required this.orderId});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final orderAsync = ref.watch(orderDetailProvider(orderId));

    return Scaffold(
      appBar: AppBar(
        title: const Text('Track Order'),
        backgroundColor: Colors.green,
        foregroundColor: Colors.white,
      ),
      body: orderAsync.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (err, _) => AsyncErrorView(
          error: err,
          onRetry: () => ref.invalidate(orderDetailProvider(orderId)),
        ),
        data: (order) {
          return SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Card(
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text('Status: ${order.status.replaceAll('_', ' ')}', style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 16)),
                        if (order.estimatedDeliveryAt != null) ...[
                          const SizedBox(height: 8),
                          Text('Estimated delivery: ${_formatDate(order.estimatedDeliveryAt!)}', style: TextStyle(color: Colors.grey[700])),
                        ],
                        if (order.driverPhone != null && order.driverPhone!.isNotEmpty) ...[
                          const SizedBox(height: 12),
                          Row(
                            children: [
                              const Icon(Icons.person, size: 20),
                              const SizedBox(width: 8),
                              const Text('Delivery partner'),
                              const Spacer(),
                              IconButton(
                                icon: const Icon(Icons.phone, color: Colors.green),
                                onPressed: () => _launchPhone(order.driverPhone!),
                              ),
                            ],
                          ),
                        ],
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 24),
                const Text('Live tracking and map will be available in a future update.', style: TextStyle(color: Colors.grey)),
              ],
            ),
          );
        },
      ),
    );
  }

  String _formatDate(DateTime d) {
    return '${d.day}/${d.month}/${d.year} ${d.hour.toString().padLeft(2, '0')}:${d.minute.toString().padLeft(2, '0')}';
  }

  Future<void> _launchPhone(String phone) async {
    final uri = Uri(scheme: 'tel', path: phone.trim());
    if (await canLaunchUrl(uri)) await launchUrl(uri);
  }
}
