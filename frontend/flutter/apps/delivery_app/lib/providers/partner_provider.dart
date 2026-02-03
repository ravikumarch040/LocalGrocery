import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:api_client/api_client.dart';
import 'api_providers.dart';

const String _keyPartnerId = 'delivery_partner_id';

/// Current delivery partner ID (from profile or dev placeholder; backend may provide via profile).
final deliveryPartnerIdProvider = FutureProvider<String?>((ref) async {
  final prefs = await SharedPreferences.getInstance();
  return prefs.getString(_keyPartnerId);
});

/// Delivery partner details (fetched when we have partner ID).
final deliveryPartnerProvider = FutureProvider<DeliveryPartnerDto?>((ref) async {
  final partnerId = await ref.watch(deliveryPartnerIdProvider.future);
  if (partnerId == null) return null;
  final service = ref.read(deliveryServiceProvider);
  final res = await service.getPartner(partnerId);
  return res.success ? res.data : null;
});

/// Set partner ID (e.g. after login if profile returns it).
Future<void> setDeliveryPartnerId(String? partnerId) async {
  final prefs = await SharedPreferences.getInstance();
  if (partnerId != null) {
    await prefs.setString(_keyPartnerId, partnerId);
  } else {
    await prefs.remove(_keyPartnerId);
  }
}
