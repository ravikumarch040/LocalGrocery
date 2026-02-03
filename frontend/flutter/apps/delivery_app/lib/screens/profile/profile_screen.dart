import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../providers/auth_provider.dart';
import '../../providers/partner_provider.dart';

class ProfileScreen extends ConsumerWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final auth = ref.watch(authProvider).value;
    final partnerAsync = ref.watch(deliveryPartnerProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Profile')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Row(
                  children: [
                    CircleAvatar(
                      radius: 32,
                      backgroundColor: Colors.blue.shade200,
                      child: Text(
                        (auth?.name ?? auth?.phone ?? 'D').substring(0, 1).toUpperCase(),
                        style: TextStyle(fontSize: 24, color: Colors.blue.shade900),
                      ),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(auth?.name ?? 'Delivery Partner', style: Theme.of(context).textTheme.titleLarge),
                          Text(auth?.phone ?? '', style: Theme.of(context).textTheme.bodyMedium?.copyWith(color: Colors.grey.shade600)),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),
            partnerAsync.when(
              data: (partner) {
                if (partner == null) return const SizedBox.shrink();
                return Card(
                  child: ListTile(
                    leading: const Icon(Icons.two_wheeler),
                    title: Text(partner.vehicleType),
                    subtitle: Text('${partner.successfulDeliveries} deliveries · ${partner.rating.toStringAsFixed(1)} rating'),
                  ),
                );
              },
              loading: () => const SizedBox.shrink(),
              error: (e, st) => const SizedBox.shrink(),
            ),
            const SizedBox(height: 16),
            ListTile(
              leading: const Icon(Icons.payments),
              title: const Text('Earnings'),
              trailing: const Icon(Icons.chevron_right),
              onTap: () => context.push('/earnings'),
            ),
            const Divider(),
            ListTile(
              leading: Icon(Icons.logout, color: Colors.red.shade400),
              title: Text('Logout', style: TextStyle(fontWeight: FontWeight.w600, color: Colors.red.shade400)),
              onTap: () async {
                await setDeliveryPartnerId(null);
                await ref.read(authProvider.notifier).logout();
                if (context.mounted) context.go('/login');
              },
            ),
          ],
        ),
      ),
    );
  }
}
