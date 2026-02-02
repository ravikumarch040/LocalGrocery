import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:models/models.dart';
import '../../providers/catalog_provider.dart';
import '../../providers/cart_provider.dart';
import '../../providers/location_provider.dart';
import '../../widgets/category_card.dart';
import '../../widgets/product_card.dart';

class HomeScreen extends ConsumerWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      backgroundColor: Colors.grey[50],
      appBar: AppBar(
        backgroundColor: Colors.green,
        foregroundColor: Colors.white,
        elevation: 0,
        titleSpacing: 0,
        title: _buildLocationAppBarTitle(context, ref),
        actions: [
          IconButton(
            icon: const Icon(Icons.shopping_cart_outlined),
            onPressed: () => context.push('/cart'),
          ),
        ],
      ),
      body: SingleChildScrollView(
        child: Column(
          children: [
            // Search Bar
            _buildSearchBar(context),
            const SizedBox(height: 16),

            // Categories Section
            _buildCategoriesSection(context, ref),
            const SizedBox(height: 24),

            // Featured Products Section
            _buildFeaturedProductsSection(context, ref),
            const SizedBox(height: 24),
          ],
        ),
      ),
    );
  }

  Widget _buildLocationAppBarTitle(BuildContext context, WidgetRef ref) {
    final locationState = ref.watch(userLocationProvider);

    return InkWell(
      onTap: () => _showLocationSelector(context, ref),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          const Icon(Icons.location_on_outlined, size: 20),
          const SizedBox(width: 8),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              const Text(
                'Deliver to',
                style: TextStyle(fontSize: 11),
              ),
              locationState.when(
                loading: () => const SizedBox(
                  height: 16,
                  width: 60,
                  child: LinearProgressIndicator(
                    backgroundColor: Colors.white24,
                  ),
                ),
                error: (_, __) => const Text(
                  'Select location',
                  style: TextStyle(
                    fontSize: 13,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                data: (value) => Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Flexible(
                      child: Text(
                        value.displayText,
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                        style: const TextStyle(
                          fontSize: 13,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ),
                    const SizedBox(width: 4),
                    const Icon(
                      Icons.keyboard_arrow_down_rounded,
                      size: 18,
                    ),
                  ],
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Future<void> _showLocationSelector(BuildContext context, WidgetRef ref) async {
    await showModalBottomSheet<void>(
      context: context,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(16)),
      ),
      builder: (context) {
        return SafeArea(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Text(
                      'Select delivery location',
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    IconButton(
                      icon: const Icon(Icons.close),
                      onPressed: () => Navigator.of(context).pop(),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                Text(
                  'Location selection is not fully wired yet.\n'
                  'In the next step, this will show saved addresses and current location.',
                  style: TextStyle(
                    fontSize: 13,
                    color: Colors.grey[700],
                  ),
                ),
                const SizedBox(height: 16),
                SizedBox(
                  width: double.infinity,
                  child: OutlinedButton.icon(
                    icon: const Icon(Icons.my_location),
                    label: const Text('Use current location'),
                    onPressed: () async {
                      await ref.read(userLocationProvider.notifier).detectCurrentLocation();
                      if (context.mounted) {
                        Navigator.of(context).pop();
                      }
                    },
                  ),
                ),
                const SizedBox(height: 8),
                SizedBox(
                  width: double.infinity,
                  child: OutlinedButton.icon(
                    icon: const Icon(Icons.add_location_alt_outlined),
                    label: const Text('Add new address'),
                    onPressed: () {
                      Navigator.of(context).pop();
                      context.push('/addresses/add');
                    },
                  ),
                ),
                const SizedBox(height: 8),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildSearchBar(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      color: Colors.white,
      child: TextField(
        decoration: InputDecoration(
          hintText: 'Search products...',
          prefixIcon: const Icon(Icons.search),
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(8),
            borderSide: BorderSide(color: Colors.grey[300]!),
          ),
          contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        ),
        textInputAction: TextInputAction.search,
        onSubmitted: (query) {
          final trimmed = query.trim();
          if (trimmed.isNotEmpty) {
            context.push('/search?q=$trimmed');
          }
        },
        onTapOutside: (_) => FocusScope.of(context).unfocus(),
      ),
    );
  }

  Widget _buildCategoriesSection(BuildContext context, WidgetRef ref) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16),
          child: Text(
            'Categories',
            style: Theme.of(context).textTheme.titleLarge,
          ),
        ),
        const SizedBox(height: 12),
        SizedBox(
          height: 120,
          child: ref.watch(categoriesProvider).when(
            loading: () => const Center(child: CircularProgressIndicator()),
            error: (err, stack) => Center(
              child: Text('Error: $err'),
            ),
            data: (categories) {
              return ListView.builder(
                scrollDirection: Axis.horizontal,
                padding: const EdgeInsets.symmetric(horizontal: 16),
                itemCount: categories.length,
                itemBuilder: (context, index) {
                  final category = categories[index];
                  return CategoryCard(
                    category: category,
                    onTap: () {
                      // TODO: Navigate to products list for this category
                    },
                  );
                },
              );
            },
          ),
        ),
      ],
    );
  }

  Widget _buildFeaturedProductsSection(BuildContext context, WidgetRef ref) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16),
          child: Text(
            'Featured Products',
            style: Theme.of(context).textTheme.titleLarge,
          ),
        ),
        const SizedBox(height: 12),
        ref.watch(featuredProductsProvider).when(
          loading: () => const Center(child: CircularProgressIndicator()),
          error: (err, stack) => Center(
            child: Text('Error: $err'),
          ),
          data: (products) {
            return GridView.builder(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              padding: const EdgeInsets.symmetric(horizontal: 16),
              gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                crossAxisCount: 2,
                childAspectRatio: 0.75,
                crossAxisSpacing: 12,
                mainAxisSpacing: 12,
              ),
              itemCount: products.length,
              itemBuilder: (context, index) {
                final product = products[index];
                return ProductCard(
                  product: product,
                  onTap: () {
                    context.push('/product/${product.id}');
                  },
                  onAddToCart: () {
                    _handleAddToCart(context, ref, product);
                  },
                );
              },
            );
          },
        ),
      ],
    );
  }

  Future<void> _handleAddToCart(
    BuildContext context,
    WidgetRef ref,
    Product product,
  ) async {
    final scaffoldMessenger = ScaffoldMessenger.of(context);

    scaffoldMessenger.showSnackBar(
      const SnackBar(
        content: Text('Adding to cart...'),
        duration: Duration(milliseconds: 800),
      ),
    );

    try {
      // Store grouping will be handled by backend based on product/store mapping.
      await ref.read(cartProvider.notifier).addItem(
            productId: product.id,
            storeId: product.categoryId, // TODO: replace with real storeId when available
            quantity: 1,
          );

      scaffoldMessenger.showSnackBar(
        const SnackBar(
          content: Text('Added to cart'),
          duration: Duration(milliseconds: 800),
        ),
      );
    } catch (_) {
      scaffoldMessenger.showSnackBar(
        const SnackBar(
          content: Text('Failed to add to cart'),
        ),
      );
    }
  }
}
