import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:models/models.dart' as models;

import '../../providers/cart_provider.dart';

class CartScreen extends ConsumerWidget {
  const CartScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final cartAsync = ref.watch(cartProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('My Cart'),
        backgroundColor: Colors.green,
        foregroundColor: Colors.white,
        elevation: 0,
      ),
      body: cartAsync.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (err, _) => Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Text('Error: $err', textAlign: TextAlign.center),
              const SizedBox(height: 16),
              ElevatedButton(
                onPressed: () => ref.read(cartProvider.notifier).refresh(),
                child: const Text('Retry'),
              ),
            ],
          ),
        ),
        data: (cart) {
          if (cart == null || cart.items.isEmpty) {
            return _buildEmptyCart(context);
          }
          return _buildCartContent(context, ref, cart);
        },
      ),
    );
  }

  Widget _buildEmptyCart(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.shopping_cart_outlined, size: 80, color: Colors.grey[400]),
            const SizedBox(height: 16),
            Text(
              'Your cart is empty',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 8),
            Text(
              'Add items from the home screen to get started',
              textAlign: TextAlign.center,
              style: TextStyle(color: Colors.grey[600]),
            ),
            const SizedBox(height: 24),
            FilledButton.icon(
              onPressed: () => context.go('/home'),
              icon: const Icon(Icons.shopping_bag_outlined),
              label: const Text('Continue Shopping'),
              style: FilledButton.styleFrom(
                backgroundColor: Colors.green,
                padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildCartContent(
    BuildContext context,
    WidgetRef ref,
    models.Cart cart,
  ) {
    final groups = _groupItemsByStore(cart.items);

    return Column(
      children: [
        Expanded(
          child: ListView(
            padding: const EdgeInsets.all(16),
            children: [
              for (final entry in groups.entries) ...[
                _StoreSectionHeader(storeId: entry.key),
                const SizedBox(height: 8),
                for (final item in entry.value) _CartItemTile(item: item, onUpdate: ref.read(cartProvider.notifier).updateItem, onRemove: ref.read(cartProvider.notifier).removeItem),
                const SizedBox(height: 16),
              ],
              const SizedBox(height: 8),
              _CouponSection(cart: cart, onApply: ref.read(cartProvider.notifier).applyCoupon, onRemoveCoupon: ref.read(cartProvider.notifier).removeCoupon),
              const SizedBox(height: 16),
            ],
          ),
        ),
        _PriceBreakdown(cart: cart),
        SafeArea(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: SizedBox(
              width: double.infinity,
              child: FilledButton(
                onPressed: () => context.push('/checkout'),
                style: FilledButton.styleFrom(
                  backgroundColor: Colors.green,
                  padding: const EdgeInsets.symmetric(vertical: 16),
                ),
                child: const Text('Proceed to Checkout'),
              ),
            ),
          ),
        ),
      ],
    );
  }

  Map<String, List<models.CartItem>> _groupItemsByStore(List<models.CartItem> items) {
    final map = <String, List<models.CartItem>>{};
    for (final item in items) {
      map.putIfAbsent(item.storeId, () => []).add(item);
    }
    return map;
  }
}

class _StoreSectionHeader extends StatelessWidget {
  final String storeId;

  const _StoreSectionHeader({required this.storeId});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 4),
      child: Row(
        children: [
          Icon(Icons.store_outlined, size: 20, color: Colors.grey[700]),
          const SizedBox(width: 8),
          Text(
            'Store',
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.w600,
                  color: Colors.grey[800],
                ),
          ),
          if (storeId.length <= 12) ...[
            const SizedBox(width: 4),
            Text('($storeId)', style: TextStyle(fontSize: 12, color: Colors.grey[600])),
          ],
        ],
      ),
    );
  }
}

class _CartItemTile extends StatelessWidget {
  final models.CartItem item;
  final void Function({required String itemId, required int quantity}) onUpdate;
  final void Function(String itemId) onRemove;

  const _CartItemTile({
    required this.item,
    required this.onUpdate,
    required this.onRemove,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    item.name,
                    style: const TextStyle(
                      fontWeight: FontWeight.w600,
                      fontSize: 14,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    '₹${item.price.toStringAsFixed(0)} × ${item.quantity}',
                    style: TextStyle(color: Colors.grey[600], fontSize: 12),
                  ),
                  const SizedBox(height: 8),
                  Row(
                    children: [
                      _QuantityChip(
                        label: '-',
                        onTap: () {
                          if (item.quantity > 1) {
                            onUpdate(itemId: item.id, quantity: item.quantity - 1);
                          } else {
                            onRemove(item.id);
                          }
                        },
                      ),
                      Padding(
                        padding: const EdgeInsets.symmetric(horizontal: 12),
                        child: Text('${item.quantity}', style: const TextStyle(fontWeight: FontWeight.w600)),
                      ),
                      _QuantityChip(
                        label: '+',
                        onTap: () => onUpdate(itemId: item.id, quantity: item.quantity + 1),
                      ),
                    ],
                  ),
                ],
              ),
            ),
            Column(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                Text(
                  '₹${item.subtotal.toStringAsFixed(0)}',
                  style: const TextStyle(
                    fontWeight: FontWeight.bold,
                    fontSize: 14,
                    color: Colors.green,
                  ),
                ),
                const SizedBox(height: 8),
                IconButton(
                  icon: Icon(Icons.delete_outline, size: 20, color: Colors.red[400]),
                  onPressed: () => onRemove(item.id),
                  padding: EdgeInsets.zero,
                  constraints: const BoxConstraints(minWidth: 32, minHeight: 32),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class _QuantityChip extends StatelessWidget {
  final String label;
  final VoidCallback onTap;

  const _QuantityChip({required this.label, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.grey[200],
      borderRadius: BorderRadius.circular(8),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(8),
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
          child: Text(label, style: const TextStyle(fontWeight: FontWeight.bold)),
        ),
      ),
    );
  }
}

class _CouponSection extends ConsumerStatefulWidget {
  final models.Cart cart;
  final Future<void> Function(String code) onApply;
  final Future<void> Function() onRemoveCoupon;

  const _CouponSection({
    required this.cart,
    required this.onApply,
    required this.onRemoveCoupon,
  });

  @override
  ConsumerState<_CouponSection> createState() => _CouponSectionState();
}

class _CouponSectionState extends ConsumerState<_CouponSection> {
  final _controller = TextEditingController();
  bool _loading = false;
  String? _error;

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  Future<void> _apply() async {
    final code = _controller.text.trim();
    if (code.isEmpty) return;
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      await widget.onApply(code);
      if (mounted) {
        _controller.clear();
        setState(() { _loading = false; });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _loading = false;
          _error = e.toString().replaceFirst('Exception: ', '');
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final hasCoupon = widget.cart.couponCode != null && widget.cart.couponCode!.isNotEmpty;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Coupon', style: Theme.of(context).textTheme.titleSmall?.copyWith(fontWeight: FontWeight.w600)),
            if (hasCoupon) ...[
              const SizedBox(height: 8),
              Row(
                children: [
                  Chip(
                    label: Text(widget.cart.couponCode!),
                    onDeleted: () => widget.onRemoveCoupon(),
                  ),
                  if (widget.cart.couponDiscount > 0)
                    Padding(
                      padding: const EdgeInsets.only(left: 8),
                      child: Text('-₹${widget.cart.couponDiscount.toStringAsFixed(0)}', style: TextStyle(color: Colors.green[700], fontWeight: FontWeight.w600)),
                    ),
                ],
              ),
            ] else ...[
              const SizedBox(height: 8),
              Row(
                children: [
                  Expanded(
                    child: TextField(
                      controller: _controller,
                      decoration: InputDecoration(
                        hintText: 'Enter coupon code',
                        border: const OutlineInputBorder(),
                        errorText: _error,
                        contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                      ),
                      onSubmitted: (_) => _apply(),
                    ),
                  ),
                  const SizedBox(width: 8),
                  FilledButton(
                    onPressed: _loading ? null : _apply,
                    style: FilledButton.styleFrom(backgroundColor: Colors.green),
                    child: _loading ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(strokeWidth: 2)) : const Text('Apply'),
                  ),
                ],
              ),
            ],
          ],
        ),
      ),
    );
  }
}

class _PriceBreakdown extends StatelessWidget {
  final models.Cart cart;

  const _PriceBreakdown({required this.cart});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.grey[100],
        border: Border(top: BorderSide(color: Colors.grey[300]!)),
      ),
      child: Column(
        children: [
          _Row(label: 'Subtotal', value: cart.subtotal),
          if (cart.discount > 0) _Row(label: 'Discount', value: -cart.discount, valueColor: Colors.green),
          if (cart.couponDiscount > 0) _Row(label: 'Coupon', value: -cart.couponDiscount, valueColor: Colors.green),
          if (cart.deliveryFee > 0) _Row(label: 'Delivery', value: cart.deliveryFee),
          if (cart.platformFee > 0) _Row(label: 'Platform fee', value: cart.platformFee),
          const Divider(height: 16),
          _Row(label: 'Total', value: cart.total, isTotal: true),
        ],
      ),
    );
  }
}

class _Row extends StatelessWidget {
  final String label;
  final double value;
  final bool isTotal;
  final Color? valueColor;

  const _Row({required this.label, required this.value, this.isTotal = false, this.valueColor});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            label,
            style: TextStyle(
              fontWeight: isTotal ? FontWeight.bold : FontWeight.w500,
              fontSize: isTotal ? 16 : 14,
            ),
          ),
          Text(
            '₹${value.toStringAsFixed(0)}',
            style: TextStyle(
              fontWeight: isTotal ? FontWeight.bold : FontWeight.w500,
              fontSize: isTotal ? 16 : 14,
              color: valueColor ?? (isTotal ? Colors.green : null),
            ),
          ),
        ],
      ),
    );
  }
}
