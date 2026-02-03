import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../providers/products_provider.dart';

class ProductsScreen extends ConsumerWidget {
  const ProductsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final productsAsync = ref.watch(retailerStoreProductsProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Inventory'),
        actions: [
          IconButton(
            icon: const Icon(Icons.edit_note),
            tooltip: 'Bulk update stock',
            onPressed: () => context.push('/inventory/bulk'),
          ),
          IconButton(
            icon: const Icon(Icons.add),
            onPressed: () => context.push('/inventory/add'),
          ),
        ],
      ),
      body: productsAsync.when(
        data: (storeProducts) {
          if (storeProducts.isEmpty) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(
                    Icons.inventory_2_outlined,
                    size: 64,
                    color: Colors.grey.shade400,
                  ),
                  const SizedBox(height: 16),
                  Text(
                    'No products yet',
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                          color: Colors.grey.shade600,
                        ),
                  ),
                  const SizedBox(height: 8),
                  FilledButton.icon(
                    onPressed: () => context.push('/inventory/add'),
                    icon: const Icon(Icons.add),
                    label: const Text('Add product'),
                  ),
                ],
              ),
            );
          }
          return RefreshIndicator(
            onRefresh: () async => ref.invalidate(retailerStoreProductsProvider),
            child: ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: storeProducts.length,
              itemBuilder: (context, index) {
                final sp = storeProducts[index];
                final product = sp.product;
                final name = product?.name ?? 'Product';
                final price = sp.storePrice ?? product?.basePrice ?? 0.0;
                return Card(
                  margin: const EdgeInsets.only(bottom: 12),
                  child: ListTile(
                    leading: product?.imageUrl != null
                        ? Image.network(
                            product!.imageUrl!,
                            width: 48,
                            height: 48,
                            fit: BoxFit.cover,
                            errorBuilder: (context, error, stackTrace) =>
                                const Icon(Icons.image_not_supported),
                          )
                        : const Icon(Icons.inventory_2_outlined),
                    title: Text(name),
                    subtitle: Text(
                      '₹${price.toStringAsFixed(0)} · Stock: ${sp.stockQuantity} · ${product?.unit ?? 'unit'}',
                    ),
                    trailing: const Icon(Icons.chevron_right),
                    onTap: () => context.push('/inventory/edit/${sp.id}'),
                  ),
                );
              },
            ),
          );
        },
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, st) => Center(
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
      floatingActionButton: FloatingActionButton(
        onPressed: () => context.push('/inventory/add'),
        child: const Icon(Icons.add),
      ),
    );
  }
}
