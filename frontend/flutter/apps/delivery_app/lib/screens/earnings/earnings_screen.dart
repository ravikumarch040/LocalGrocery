import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../providers/delivery_provider.dart';
import '../../providers/partner_provider.dart';

class EarningsScreen extends ConsumerWidget {
  const EarningsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final myDeliveriesAsync = ref.watch(myDeliveriesProvider);
    final partnerAsync = ref.watch(deliveryPartnerProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Earnings')),
      body: partnerAsync.when(
        data: (partner) {
          final completed = myDeliveriesAsync.valueOrNull?.where((d) => d.status == 'DELIVERED').toList() ?? [];
          final totalEarnings = completed.fold<double>(0, (s, d) => s + (d.deliveryFee ?? 0));

          return SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Card(
                  child: Padding(
                    padding: const EdgeInsets.all(24),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text('Today', style: Theme.of(context).textTheme.titleMedium?.copyWith(color: Colors.grey.shade600)),
                        const SizedBox(height: 8),
                        Text(
                          '₹ ${totalEarnings.toStringAsFixed(0)}',
                          style: Theme.of(context).textTheme.headlineMedium?.copyWith(fontWeight: FontWeight.bold, color: Colors.green.shade700),
                        ),
                        const SizedBox(height: 16),
                        if (partner != null)
                          Text('${partner.successfulDeliveries} deliveries · Rating ${partner.rating.toStringAsFixed(1)}', style: Theme.of(context).textTheme.bodySmall),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 24),
                Text('Recent trips', style: Theme.of(context).textTheme.titleMedium),
                const SizedBox(height: 8),
                myDeliveriesAsync.when(
                  data: (list) {
                    final delivered = list.where((d) => d.status == 'DELIVERED').take(10).toList();
                    if (delivered.isEmpty) {
                      return Card(
                        child: Padding(
                          padding: const EdgeInsets.all(16),
                          child: Text('No completed deliveries yet', style: Theme.of(context).textTheme.bodyMedium?.copyWith(color: Colors.grey.shade600)),
                        ),
                      );
                    }
                    return Column(
                      children: delivered.map((d) => Card(
                        margin: const EdgeInsets.only(bottom: 8),
                        child: ListTile(
                          leading: const Icon(Icons.delivery_dining),
                          title: Text(d.deliveryAddress),
                          subtitle: Text(d.status),
                          trailing: Text('₹${d.deliveryFee?.toStringAsFixed(0) ?? '—'}'),
                        ),
                      )).toList(),
                    );
                  },
                  loading: () => const Center(child: CircularProgressIndicator()),
                  error: (e, st) => Text('Error: $e'),
                ),
              ],
            ),
          );
        },
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, st) => Center(child: Text('Error: $e')),
      ),
    );
  }
}
