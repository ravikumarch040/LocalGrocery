import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:api_client/api_client.dart';
import 'api_providers.dart';
import 'store_provider.dart';

/// Store products for retailer's store (from GET /api/v1/store-products/store/{store_id})
final retailerStoreProductsProvider =
    FutureProvider.autoDispose<List<StoreProduct>>((ref) async {
  final store = await ref.watch(retailerStoreProvider.future);
  if (store == null) return [];
  final catalog = ref.read(catalogServiceProvider);
  final res = await catalog.listStoreProducts(storeId: store.id, pageSize: 100);
  if (!res.success || res.data == null) return [];
  return res.data!;
});
