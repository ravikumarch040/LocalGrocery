import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:api_client/api_client.dart';
import 'api_providers.dart';
import 'partner_provider.dart';

/// Available deliveries (PENDING, unassigned) for driver to accept.
final availableDeliveriesProvider = FutureProvider.autoDispose<List<DeliveryDto>>((ref) async {
  final service = ref.read(deliveryServiceProvider);
  final res = await service.listDeliveries(status: 'PENDING', limit: 50);
  return res.success && res.data != null ? res.data! : [];
});

/// My deliveries (assigned to current partner).
final myDeliveriesProvider = FutureProvider.autoDispose<List<DeliveryDto>>((ref) async {
  final partnerId = await ref.watch(deliveryPartnerIdProvider.future);
  if (partnerId == null) return [];
  final service = ref.read(deliveryServiceProvider);
  final res = await service.listDeliveries(partnerId: partnerId, limit: 50);
  return res.success && res.data != null ? res.data! : [];
});

/// Single delivery by ID.
final deliveryDetailProvider = FutureProvider.autoDispose.family<DeliveryDto?, String>((ref, deliveryId) async {
  final service = ref.read(deliveryServiceProvider);
  final res = await service.getDelivery(deliveryId);
  return res.success ? res.data : null;
});
