import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:models/models.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'api_providers.dart';
import 'auth_provider.dart';

const String _keyStoreId = 'retailer_store_id';
const String _keyStoreName = 'retailer_store_name';

final retailerStoreIdProvider = FutureProvider<String?>((ref) async {
  final prefs = await SharedPreferences.getInstance();
  return prefs.getString(_keyStoreId);
});

final retailerStoreProvider = FutureProvider<Store?>((ref) async {
  final auth = await ref.watch(authProvider.future);
  if (auth == null) return null;

  final storeId = await ref.watch(retailerStoreIdProvider.future);
  if (storeId != null) {
    final catalog = ref.read(catalogServiceProvider);
    final res = await catalog.getStore(storeId);
    if (res.success && res.data != null) return res.data;
  }

  // Stub: try a default store ID for development
  const stubStoreId = '00000000-0000-0000-0000-000000000001';
  final catalog = ref.read(catalogServiceProvider);
  final res = await catalog.getStore(stubStoreId);
  if (res.success && res.data != null) {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_keyStoreId, res.data!.id);
    await prefs.setString(_keyStoreName, res.data!.name);
    return res.data;
  }
  return null;
});
