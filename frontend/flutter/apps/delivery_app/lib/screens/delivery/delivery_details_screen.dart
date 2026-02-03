import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:geolocator/geolocator.dart';
import '../../providers/delivery_provider.dart';
import '../../providers/partner_provider.dart';
import '../../providers/api_providers.dart';

class DeliveryDetailsScreen extends ConsumerWidget {
  final String deliveryId;

  const DeliveryDetailsScreen({super.key, required this.deliveryId});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final deliveryAsync = ref.watch(deliveryDetailProvider(deliveryId));

    return Scaffold(
      appBar: AppBar(title: Text('Delivery #${deliveryId.substring(0, 8)}')),
      body: deliveryAsync.when(
        data: (d) {
          if (d == null) {
            return const Center(child: Text('Delivery not found'));
          }
          final isAssigned = d.deliveryPartnerId != null;
          final canAccept = d.status == 'PENDING' && !isAssigned;
          final canPickUp = d.status == 'ASSIGNED';
          final canDeliver = d.status == 'PICKED_UP' || d.status == 'IN_TRANSIT';

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
                        Text(d.status, style: Theme.of(context).textTheme.titleMedium?.copyWith(color: Colors.blue.shade700, fontWeight: FontWeight.bold)),
                        const SizedBox(height: 12),
                        _Row(label: 'Pickup', value: d.pickupAddress, icon: Icons.store),
                        const SizedBox(height: 8),
                        _Row(label: 'Delivery', value: d.deliveryAddress, icon: Icons.location_on),
                        if (d.distanceKm != null) ...[
                          const SizedBox(height: 8),
                          _Row(label: 'Distance', value: '${d.distanceKm!.toStringAsFixed(1)} km', icon: Icons.straighten),
                        ],
                        if (d.deliveryFee != null) ...[
                          const SizedBox(height: 8),
                          _Row(label: 'Earnings', value: '₹${d.deliveryFee!.toStringAsFixed(0)}', icon: Icons.currency_rupee),
                        ],
                        if (d.deliveryInstructions != null && d.deliveryInstructions!.isNotEmpty) ...[
                          const SizedBox(height: 8),
                          _Row(label: 'Instructions', value: d.deliveryInstructions!, icon: Icons.info_outline),
                        ],
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 16),
                if (canAccept)
                  FilledButton.icon(
                    onPressed: () => _accept(context, ref),
                    icon: const Icon(Icons.check),
                    label: const Text('Accept delivery'),
                  ),
                if (canPickUp)
                  FilledButton.icon(
                    onPressed: () => _updateStatus(context, ref, 'PICKED_UP'),
                    icon: const Icon(Icons.inventory_2),
                    label: const Text('Mark picked up'),
                  ),
                if (canDeliver)
                  FilledButton.icon(
                    onPressed: () => context.push('/delivery/$deliveryId/proof'),
                    icon: const Icon(Icons.done_all),
                    label: const Text('Mark delivered'),
                  ),
                const SizedBox(height: 16),
                OutlinedButton.icon(
                  onPressed: () => context.push('/delivery/$deliveryId/map'),
                  icon: const Icon(Icons.map),
                  label: const Text('Show map'),
                ),
                OutlinedButton.icon(
                  onPressed: () => _openMaps(d.deliveryAddress),
                  icon: const Icon(Icons.directions),
                  label: const Text('Open in Maps'),
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

  Future<void> _accept(BuildContext context, WidgetRef ref) async {
    final partnerId = await ref.read(deliveryPartnerIdProvider.future);
    if (partnerId == null) return;
    final service = ref.read(deliveryServiceProvider);
    final res = await service.assignDelivery(deliveryId: deliveryId, deliveryPartnerId: partnerId);
    if (!context.mounted) return;
    if (res.success) {
      ref.invalidate(deliveryDetailProvider(deliveryId));
      ref.invalidate(availableDeliveriesProvider);
      ref.invalidate(myDeliveriesProvider);
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Accepted')));
    } else {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(res.message ?? 'Failed'), backgroundColor: Colors.red));
    }
  }

  Future<void> _updateStatus(BuildContext context, WidgetRef ref, String status) async {
    Map<String, dynamic>? location;
    try {
      final pos = await Geolocator.getCurrentPosition(
        locationSettings: const LocationSettings(accuracy: LocationAccuracy.medium),
      );
      location = {'lat': pos.latitude, 'lng': pos.longitude};
      final partnerId = await ref.read(deliveryPartnerIdProvider.future);
      if (partnerId != null) {
        final service = ref.read(deliveryServiceProvider);
        await service.updatePartnerLocation(
          partnerId: partnerId,
          lat: pos.latitude,
          lng: pos.longitude,
        );
      }
    } catch (_) {}
    final service = ref.read(deliveryServiceProvider);
    final res = await service.updateDeliveryStatus(
      deliveryId: deliveryId,
      status: status,
      location: location,
    );
    if (!context.mounted) return;
    if (res.success) {
      ref.invalidate(deliveryDetailProvider(deliveryId));
      ref.invalidate(myDeliveriesProvider);
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Status: $status')));
    } else {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(res.message ?? 'Failed'), backgroundColor: Colors.red));
    }
  }

  Future<void> _openMaps(String address) async {
    final uri = Uri.parse('https://www.google.com/maps/search/?api=1&query=${Uri.encodeComponent(address)}');
    if (await canLaunchUrl(uri)) {
      await launchUrl(uri, mode: LaunchMode.externalApplication);
    }
  }
}

class _Row extends StatelessWidget {
  final String label;
  final String value;
  final IconData icon;

  const _Row({required this.label, required this.value, required this.icon});

  @override
  Widget build(BuildContext context) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Icon(icon, size: 20, color: Colors.grey.shade600),
        const SizedBox(width: 8),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(label, style: Theme.of(context).textTheme.bodySmall?.copyWith(color: Colors.grey.shade600)),
              Text(value, style: Theme.of(context).textTheme.bodyMedium),
            ],
          ),
        ),
      ],
    );
  }
}
