import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../providers/auth_provider.dart';
import '../../providers/store_provider.dart';

class ProfileScreen extends ConsumerWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final auth = ref.watch(authProvider).value;
    final storeAsync = ref.watch(retailerStoreProvider);

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
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        CircleAvatar(
                          radius: 32,
                          backgroundColor: Colors.amber.shade200,
                          child: Text(
                            (auth?.name ?? auth?.phone ?? 'R').substring(0, 1).toUpperCase(),
                            style: TextStyle(
                              fontSize: 24,
                              color: Colors.amber.shade900,
                            ),
                          ),
                        ),
                        const SizedBox(width: 16),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                auth?.name ?? 'Retailer',
                                style: Theme.of(context).textTheme.titleLarge,
                              ),
                              Text(
                                auth?.phone ?? '',
                                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                                      color: Colors.grey.shade600,
                                    ),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),
            storeAsync.when(
              data: (store) {
                if (store == null) return const SizedBox.shrink();
                return Card(
                  child: ListTile(
                    leading: const Icon(Icons.store),
                    title: Text(store.name),
                    subtitle: Text(store.description),
                    trailing: const Icon(Icons.chevron_right),
                  ),
                );
              },
              loading: () => const SizedBox.shrink(),
              error: (e, st) => const SizedBox.shrink(),
            ),
            const SizedBox(height: 16),
            ListTile(
              leading: const Icon(Icons.verified_user_outlined),
              title: const Text('KYC & documents'),
              subtitle: const Text('Complete verification'),
              trailing: const Icon(Icons.chevron_right),
              onTap: () => context.push('/kyc'),
            ),
            const Divider(),
            ListTile(
              leading: const Icon(Icons.account_balance_outlined),
              title: const Text('Bank details'),
              subtitle: const Text('Settlement account'),
              trailing: const Icon(Icons.chevron_right),
              onTap: () {},
            ),
            ListTile(
              leading: const Icon(Icons.settings_outlined),
              title: const Text('Settings'),
              trailing: const Icon(Icons.chevron_right),
              onTap: () {},
            ),
            const Divider(),
            ListTile(
              leading: Icon(Icons.logout, color: Colors.red.shade400),
              title: Text(
                'Logout',
                style: TextStyle(
                  fontWeight: FontWeight.w600,
                  color: Colors.red.shade400,
                ),
              ),
              onTap: () async {
                final notifier = ref.read(authProvider.notifier);
                await notifier.logout();
                if (context.mounted) context.go('/login');
              },
            ),
          ],
        ),
      ),
    );
  }
}
