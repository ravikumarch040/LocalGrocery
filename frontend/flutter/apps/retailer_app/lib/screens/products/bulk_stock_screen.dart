import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:api_client/api_client.dart';
import '../../providers/api_providers.dart';
import '../../providers/products_provider.dart';

class BulkStockScreen extends ConsumerStatefulWidget {
  const BulkStockScreen({super.key});

  @override
  ConsumerState<BulkStockScreen> createState() => _BulkStockScreenState();
}

class _BulkStockScreenState extends ConsumerState<BulkStockScreen> {
  /// storeProductId -> (stock, price) - only entries that user changed
  final Map<String, ({int stock, double price})> _edits = {};
  bool _saving = false;

  void _setStock(String storeProductId, int stock, double price) {
    setState(() {
      _edits[storeProductId] = (stock: stock, price: price);
    });
  }

  void _setPrice(String storeProductId, int stock, double price) {
    setState(() {
      _edits[storeProductId] = (stock: stock, price: price);
    });
  }

  Future<void> _saveAll(List<StoreProduct> list) async {
    if (_edits.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('No changes to save')),
      );
      return;
    }
    setState(() => _saving = true);
    final catalog = ref.read(catalogServiceProvider);
    int ok = 0, fail = 0;
    for (final entry in _edits.entries) {
      final res = await catalog.updateStoreProduct(
        storeProductId: entry.key,
        stockQuantity: entry.value.stock,
        storePrice: entry.value.price,
      );
      if (res.success) {
        ok++;
      } else {
        fail++;
      }
    }
    if (!mounted) return;
    setState(() {
      _saving = false;
      _edits.clear();
    });
    ref.invalidate(retailerStoreProductsProvider);
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(
          fail > 0 ? 'Updated $ok. Failed: $fail' : 'Updated $ok product(s)',
        ),
      ),
    );
    if (fail == 0) context.pop();
  }

  @override
  Widget build(BuildContext context) {
    final productsAsync = ref.watch(retailerStoreProductsProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Bulk stock update'),
        leading: IconButton(
          icon: const Icon(Icons.close),
          onPressed: () => context.pop(),
        ),
      ),
      body: productsAsync.when(
        data: (storeProducts) {
          if (storeProducts.isEmpty) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.inventory_2_outlined, size: 64, color: Colors.grey.shade400),
                  const SizedBox(height: 16),
                  Text(
                    'Add products first',
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(color: Colors.grey.shade600),
                  ),
                  const SizedBox(height: 16),
                  FilledButton(
                    onPressed: () => context.pop(),
                    child: const Text('Back to inventory'),
                  ),
                ],
              ),
            );
          }
          return Column(
            children: [
              Padding(
                padding: const EdgeInsets.all(16),
                child: Text(
                  'Edit stock and price below, then tap Save. Only changed rows are updated.',
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(color: Colors.grey.shade700),
                ),
              ),
              Expanded(
                child: ListView.builder(
                  padding: const EdgeInsets.symmetric(horizontal: 16),
                  itemCount: storeProducts.length,
                  itemBuilder: (context, index) {
                    final sp = storeProducts[index];
                    final product = sp.product;
                    final name = product?.name ?? 'Product';
                    final currentStock = sp.stockQuantity;
                    final currentPrice = sp.storePrice ?? product?.basePrice ?? 0.0;
                    final edit = _edits[sp.id];
                    final stock = edit?.stock ?? currentStock;
                    final price = edit?.price ?? currentPrice;
                    return Card(
                      key: ValueKey('${sp.id}_${sp.stockQuantity}_${sp.storePrice}'),
                      margin: const EdgeInsets.only(bottom: 12),
                      child: Padding(
                        padding: const EdgeInsets.all(12),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              name,
                              style: Theme.of(context).textTheme.titleSmall,
                            ),
                            const SizedBox(height: 12),
                            Row(
                              children: [
                                Expanded(
                                  child: TextFormField(
                                    initialValue: stock.toString(),
                                    decoration: const InputDecoration(
                                      labelText: 'Stock',
                                      isDense: true,
                                      border: OutlineInputBorder(),
                                    ),
                                    keyboardType: TextInputType.number,
                                    onChanged: (v) {
                                      final s = int.tryParse(v) ?? currentStock;
                                      _setStock(sp.id, s, edit?.price ?? currentPrice);
                                    },
                                  ),
                                ),
                                const SizedBox(width: 12),
                                Expanded(
                                  child: TextFormField(
                                    initialValue: price.toStringAsFixed(0),
                                    decoration: const InputDecoration(
                                      labelText: 'Price (₹)',
                                      isDense: true,
                                      border: OutlineInputBorder(),
                                    ),
                                    keyboardType: TextInputType.number,
                                    onChanged: (v) {
                                      final p = double.tryParse(v.replaceAll(',', '.')) ?? currentPrice;
                                      _setPrice(sp.id, edit?.stock ?? currentStock, p);
                                    },
                                  ),
                                ),
                              ],
                            ),
                          ],
                        ),
                      ),
                    );
                  },
                ),
              ),
              Padding(
                padding: const EdgeInsets.all(16),
                child: FilledButton(
                  onPressed: _saving ? null : () => _saveAll(storeProducts),
                  style: FilledButton.styleFrom(
                    minimumSize: const Size(double.infinity, 48),
                  ),
                  child: _saving
                      ? const SizedBox(
                          height: 24,
                          width: 24,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        )
                      : Text(_edits.isEmpty ? 'No changes' : 'Save ${_edits.length} change(s)'),
                ),
              ),
            ],
          );
        },
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(Icons.error_outline, size: 48, color: Colors.red.shade300),
              const SizedBox(height: 16),
              Padding(
                padding: const EdgeInsets.all(24),
                child: Text('Error: $e', textAlign: TextAlign.center),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
