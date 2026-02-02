import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:models/models.dart' as models;

import '../../providers/address_provider.dart';

class AddressListScreen extends ConsumerWidget {
  const AddressListScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final addressesAsync = ref.watch(savedAddressesProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Saved Addresses'),
        backgroundColor: Colors.green,
        foregroundColor: Colors.white,
        actions: [
          TextButton(
            onPressed: () => context.push('/addresses/add'),
            child: const Text('Add new', style: TextStyle(color: Colors.white)),
          ),
        ],
      ),
      body: addressesAsync.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (err, _) => Center(child: Text('Error: $err')),
        data: (addresses) {
          if (addresses.isEmpty) {
            return Center(
              child: Padding(
                padding: const EdgeInsets.all(24),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(Icons.location_off_outlined, size: 64, color: Colors.grey[400]),
                    const SizedBox(height: 16),
                    Text(
                      'No saved addresses',
                      style: Theme.of(context).textTheme.titleLarge,
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'Add an address for faster checkout',
                      textAlign: TextAlign.center,
                      style: TextStyle(color: Colors.grey[600]),
                    ),
                    const SizedBox(height: 24),
                    FilledButton.icon(
                      onPressed: () => context.push('/addresses/add'),
                      icon: const Icon(Icons.add_location_alt),
                      label: const Text('Add Address'),
                      style: FilledButton.styleFrom(backgroundColor: Colors.green),
                    ),
                  ],
                ),
              ),
            );
          }
          return ListView.builder(
            padding: const EdgeInsets.all(16),
            itemCount: addresses.length,
            itemBuilder: (context, index) {
              final a = addresses[index];
              return _AddressCard(
                address: a,
                onSetDefault: () => ref.read(savedAddressesProvider.notifier).setDefault(a.id),
                onRemove: () => ref.read(savedAddressesProvider.notifier).removeAddress(a.id),
              );
            },
          );
        },
      ),
      floatingActionButton: addressesAsync.value != null && addressesAsync.value!.isNotEmpty
          ? FloatingActionButton.extended(
              onPressed: () => context.push('/addresses/add'),
              icon: const Icon(Icons.add),
              label: const Text('Add Address'),
              backgroundColor: Colors.green,
            )
          : null,
    );
  }
}

class _AddressCard extends StatelessWidget {
  final models.Address address;
  final VoidCallback onSetDefault;
  final VoidCallback onRemove;

  const _AddressCard({
    required this.address,
    required this.onSetDefault,
    required this.onRemove,
  });

  @override
  Widget build(BuildContext context) {
    final parts = [
      address.addressLine1,
      if (address.addressLine2 != null && address.addressLine2!.isNotEmpty) address.addressLine2,
      '${address.city}, ${address.state} - ${address.pinCode}',
      address.country,
    ];
    final lines = parts.where((e) => e != null && e.toString().isNotEmpty).map((e) => e.toString()).toList().join(', ');

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: ListTile(
        contentPadding: const EdgeInsets.all(16),
        title: Row(
          children: [
            Text(
              address.label,
              style: const TextStyle(fontWeight: FontWeight.w600),
            ),
            if (address.isDefault) ...[
              const SizedBox(width: 8),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                decoration: BoxDecoration(
                  color: Colors.green[100],
                  borderRadius: BorderRadius.circular(4),
                ),
                child: Text(
                  'Default',
                  style: TextStyle(fontSize: 11, color: Colors.green[800], fontWeight: FontWeight.w600),
                ),
              ),
            ],
          ],
        ),
        subtitle: Padding(
          padding: const EdgeInsets.only(top: 6),
          child: Text(lines, style: TextStyle(fontSize: 13, color: Colors.grey[700])),
        ),
        trailing: PopupMenuButton<String>(
          onSelected: (value) {
            if (value == 'default') onSetDefault();
            if (value == 'remove') onRemove();
          },
          itemBuilder: (context) => [
            if (!address.isDefault) const PopupMenuItem(value: 'default', child: Text('Set as default')),
            const PopupMenuItem(value: 'remove', child: Text('Remove')),
          ],
        ),
      ),
    );
  }
}
