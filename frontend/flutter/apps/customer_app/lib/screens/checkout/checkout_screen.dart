import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:models/models.dart' as models;
import 'package:razorpay_flutter/razorpay_flutter.dart';
import 'package:core/core.dart';

import '../../providers/address_provider.dart';
import '../../providers/auth_provider.dart';
import '../../providers/cart_provider.dart';
import '../../providers/api_providers.dart';

class CheckoutScreen extends ConsumerStatefulWidget {
  const CheckoutScreen({super.key});

  @override
  ConsumerState<CheckoutScreen> createState() => _CheckoutScreenState();
}

class _CheckoutScreenState extends ConsumerState<CheckoutScreen> {
  models.Address? _selectedAddress;
  String _paymentMethod = 'cod';
  final _instructions = TextEditingController();
  bool _placing = false;
  String? _error;
  late final Razorpay _razorpay;
  _PendingOrderPayload? _pendingOrderPayload;

  @override
  void initState() {
    super.initState();
    _razorpay = Razorpay();
    _razorpay.on(Razorpay.EVENT_PAYMENT_SUCCESS, _handlePaymentSuccess);
    _razorpay.on(Razorpay.EVENT_PAYMENT_ERROR, _handlePaymentError);
  }

  @override
  void dispose() {
    _razorpay.clear();
    _instructions.dispose();
    super.dispose();
  }

  void _handlePaymentSuccess(PaymentSuccessResponse response) {
    if (_pendingOrderPayload == null) return;
    _createOrderAfterPayment();
  }

  void _handlePaymentError(PaymentFailureResponse response) {
    if (!mounted) return;
    setState(() {
      _placing = false;
      _error = response.message ?? 'Payment failed';
    });
    _pendingOrderPayload = null;
  }

  Future<void> _createOrderAfterPayment() async {
    final payload = _pendingOrderPayload;
    if (payload == null) return;
    _pendingOrderPayload = null;

    final orderService = ref.read(orderServiceProvider);
    final response = await orderService.createOrderFromCart(
      customerId: payload.customerId,
      storeId: payload.storeId,
      items: payload.items,
      deliveryAddress: payload.deliveryAddress,
      paymentMethod: 'ONLINE',
      notes: payload.notes,
    );

    if (response.success && response.data != null) {
      await ref.read(cartProvider.notifier).refresh();
      if (mounted) {
        setState(() => _placing = false);
        context.go('/orders/${response.data!.id}');
      }
    } else {
      if (mounted) {
        setState(() {
          _placing = false;
          _error = response.message ?? 'Order creation failed after payment';
        });
      }
    }
  }

  Future<void> _placeOrder() async {
    final cartAsync = ref.read(cartProvider);
    final cart = cartAsync.valueOrNull;
    if (cart == null || cart.items.isEmpty) {
      setState(() => _error = 'Cart is empty');
      return;
    }
    if (_selectedAddress == null) {
      setState(() => _error = 'Please select a delivery address');
      return;
    }

    setState(() {
      _error = null;
      _placing = true;
    });

    final user = ref.read(authProvider).value;
    final customerId = user?.id ?? 'guest';
    final orderService = ref.read(orderServiceProvider);
    final items = cart.items
        .map((e) => {
              'product_id': e.productId,
              'product_name': e.name,
              'quantity': e.quantity,
              'unit_price': e.price,
            })
        .toList();
    final storeId = cart.items.first.storeId;
    final deliveryAddress = {
      'street': _selectedAddress!.addressLine1,
      'city': _selectedAddress!.city,
      'pincode': _selectedAddress!.pinCode,
    };
    final notes = _instructions.text.trim().isEmpty ? null : _instructions.text.trim();

    // Online payment: open Razorpay first, create order on success
    if (_paymentMethod == 'online') {
      final key = AppConfig.razorpayKeyId;
      if (key.isEmpty) {
        setState(() {
          _placing = false;
          _error = 'Razorpay not configured. Add RAZORPAY_KEY_ID to .env or use COD.';
        });
        return;
      }
      _pendingOrderPayload = _PendingOrderPayload(
        customerId: customerId,
        storeId: storeId,
        items: items,
        deliveryAddress: deliveryAddress,
        notes: notes,
      );
      try {
        final amountPaise = (cart.total * 100).round();
        _razorpay.open({
          'key': key,
          'amount': amountPaise,
          'name': 'LocalGrocery',
          'description': 'Order payment',
          'prefill': {
            'contact': user?.phone ?? '',
            'email': user?.email ?? '',
          },
        });
      } catch (e) {
        setState(() {
          _placing = false;
          _error = e.toString().replaceFirst('Exception: ', '');
        });
        _pendingOrderPayload = null;
      }
      return;
    }

    // COD: create order directly
    try {
      final response = await orderService.createOrderFromCart(
        customerId: customerId,
        storeId: storeId,
        items: items,
        deliveryAddress: deliveryAddress,
        paymentMethod: 'COD',
        notes: notes,
      );

      if (response.success && response.data != null) {
        await ref.read(cartProvider.notifier).refresh();
        if (mounted) {
          setState(() => _placing = false);
          context.go('/orders/${response.data!.id}');
        }
      } else {
        setState(() {
          _placing = false;
          _error = response.message ?? 'Failed to place order';
        });
      }
    } catch (e) {
      setState(() {
        _placing = false;
        _error = e.toString().replaceFirst('Exception: ', '');
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final cartAsync = ref.watch(cartProvider);
    final addressesAsync = ref.watch(savedAddressesProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Checkout'),
        backgroundColor: Colors.green,
        foregroundColor: Colors.white,
      ),
      body: cartAsync.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (err, _) => AsyncErrorView(
          error: err,
          onRetry: () => ref.invalidate(cartProvider),
        ),
        data: (cart) {
          if (cart == null || cart.items.isEmpty) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Text('Your cart is empty'),
                  const SizedBox(height: 16),
                  FilledButton(
                    onPressed: () => context.go('/cart'),
                    style: FilledButton.styleFrom(backgroundColor: Colors.green),
                    child: const Text('Go to Cart'),
                  ),
                ],
              ),
            );
          }

          final addrs = addressesAsync.valueOrNull;
          if (addrs != null && addrs.isNotEmpty) {
            try {
              _selectedAddress ??= addrs.firstWhere((a) => a.isDefault);
            } catch (_) {
              _selectedAddress ??= addrs.first;
            }
          }

          return SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Delivery address', style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w600)),
                const SizedBox(height: 8),
                addressesAsync.when(
                  loading: () => const CircularProgressIndicator(),
                  error: (e, _) => AsyncErrorView(
                    error: e,
                    compact: true,
                    onRetry: () => ref.invalidate(savedAddressesProvider),
                  ),
                  data: (addresses) {
                    if (addresses.isEmpty) {
                      return Card(
                        child: Padding(
                          padding: const EdgeInsets.all(16),
                          child: Column(
                            children: [
                              const Text('No saved addresses'),
                              const SizedBox(height: 8),
                              FilledButton(
                                onPressed: () => context.push('/addresses/add'),
                                style: FilledButton.styleFrom(backgroundColor: Colors.green),
                                child: const Text('Add Address'),
                              ),
                            ],
                          ),
                        ),
                      );
                    }
                    return Column(
                      children: addresses.map((a) {
                        final selected = _selectedAddress?.id == a.id;
                        return RadioListTile<models.Address>(
                          title: Text(a.label),
                          subtitle: Text('${a.addressLine1}, ${a.city} - ${a.pinCode}'),
                          value: a,
                          groupValue: _selectedAddress,
                          onChanged: (v) => setState(() => _selectedAddress = v),
                          activeColor: Colors.green,
                        );
                      }).toList(),
                    );
                  },
                ),
                const SizedBox(height: 8),
                TextButton.icon(
                  onPressed: () => context.push('/addresses'),
                  icon: const Icon(Icons.list_alt),
                  label: const Text('Manage addresses'),
                ),
                const SizedBox(height: 24),
                Text('Payment method', style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w600)),
                const SizedBox(height: 8),
                RadioListTile<String>(
                  title: const Text('Cash on Delivery (COD)'),
                  value: 'cod',
                  groupValue: _paymentMethod,
                  onChanged: (v) => setState(() => _paymentMethod = v ?? 'cod'),
                  activeColor: Colors.green,
                ),
                RadioListTile<String>(
                  title: const Text('Online payment'),
                  value: 'online',
                  groupValue: _paymentMethod,
                  onChanged: (v) => setState(() => _paymentMethod = v ?? 'online'),
                  activeColor: Colors.green,
                ),
                const SizedBox(height: 24),
                Text('Delivery instructions (optional)', style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w600)),
                const SizedBox(height: 8),
                TextField(
                  controller: _instructions,
                  decoration: const InputDecoration(
                    hintText: 'e.g. Leave at door',
                    border: OutlineInputBorder(),
                  ),
                  maxLines: 2,
                ),
                const SizedBox(height: 24),
                Text('Order summary', style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w600)),
                const SizedBox(height: 8),
                _OrderSummary(cart: cart),
                if (_error != null) ...[
                  const SizedBox(height: 16),
                  Text(_error!, style: const TextStyle(color: Colors.red)),
                ],
                const SizedBox(height: 24),
                SizedBox(
                  width: double.infinity,
                  child: FilledButton(
                    onPressed: _placing ? null : _placeOrder,
                    style: FilledButton.styleFrom(
                      backgroundColor: Colors.green,
                      padding: const EdgeInsets.symmetric(vertical: 16),
                    ),
                    child: _placing
                        ? const SizedBox(height: 24, width: 24, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                        : const Text('Place Order'),
                  ),
                ),
              ],
            ),
          );
        },
      ),
    );
  }
}

class _OrderSummary extends StatelessWidget {
  final models.Cart cart;

  const _OrderSummary({required this.cart});

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            _Row(label: 'Subtotal', value: cart.subtotal),
            if (cart.couponDiscount > 0) _Row(label: 'Coupon', value: -cart.couponDiscount, valueColor: Colors.green),
            if (cart.deliveryFee > 0) _Row(label: 'Delivery', value: cart.deliveryFee),
            if (cart.platformFee > 0) _Row(label: 'Platform fee', value: cart.platformFee),
            const Divider(height: 16),
            _Row(label: 'Total', value: cart.total, isTotal: true),
          ],
        ),
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
          Text(label, style: TextStyle(fontWeight: isTotal ? FontWeight.bold : FontWeight.w500)),
          Text(
            '₹${value.toStringAsFixed(0)}',
            style: TextStyle(fontWeight: isTotal ? FontWeight.bold : FontWeight.w500, color: valueColor ?? (isTotal ? Colors.green : null)),
          ),
        ],
      ),
    );
  }
}

/// Stored when opening Razorpay so we can create order on payment success.
class _PendingOrderPayload {
  final String customerId;
  final String storeId;
  final List<Map<String, dynamic>> items;
  final Map<String, dynamic> deliveryAddress;
  final String? notes;

  _PendingOrderPayload({
    required this.customerId,
    required this.storeId,
    required this.items,
    required this.deliveryAddress,
    this.notes,
  });
}
