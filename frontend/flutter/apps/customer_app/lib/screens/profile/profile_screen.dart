import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../providers/auth_provider.dart';

class ProfileScreen extends ConsumerWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final authAsync = ref.watch(authProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Profile'),
        backgroundColor: Colors.green,
        foregroundColor: Colors.white,
      ),
      body: authAsync.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (err, _) => Center(child: Text('Error: $err')),
        data: (user) {
          if (user == null) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Text('You are not logged in'),
                  const SizedBox(height: 16),
                  FilledButton(
                    onPressed: () => context.go('/login'),
                    style: FilledButton.styleFrom(backgroundColor: Colors.green),
                    child: const Text('Login'),
                  ),
                ],
              ),
            );
          }

          return SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: Column(
              children: [
                const SizedBox(height: 16),
                CircleAvatar(
                  radius: 48,
                  backgroundColor: Colors.green[100],
                  child: user.avatar != null && user.avatar!.isNotEmpty
                      ? null
                      : Text(
                          (user.name?.isNotEmpty == true ? user.name![0] : user.phone.isNotEmpty ? user.phone[0] : '?').toUpperCase(),
                          style: TextStyle(fontSize: 32, color: Colors.green[800], fontWeight: FontWeight.w600),
                        ),
                ),
                const SizedBox(height: 12),
                Text(
                  user.name ?? 'User',
                  style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.w600),
                ),
                if (user.phone.isNotEmpty)
                  Text(user.phone, style: TextStyle(color: Colors.grey[600])),
                if (user.email != null && user.email!.isNotEmpty)
                  Text(user.email!, style: TextStyle(color: Colors.grey[600])),
                const SizedBox(height: 24),
                _MenuItem(
                  icon: Icons.edit_outlined,
                  label: 'Edit profile',
                  onTap: () {
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text('Edit profile coming soon')),
                    );
                  },
                ),
                _MenuItem(
                  icon: Icons.location_on_outlined,
                  label: 'Saved addresses',
                  onTap: () => context.push('/addresses'),
                ),
                _MenuItem(
                  icon: Icons.receipt_long_outlined,
                  label: 'Order history',
                  onTap: () => context.push('/orders'),
                ),
                _MenuItem(
                  icon: Icons.account_balance_wallet_outlined,
                  label: 'Wallet & rewards',
                  onTap: () => context.push('/profile/wallet'),
                ),
                _MenuItem(
                  icon: Icons.settings_outlined,
                  label: 'Settings',
                  onTap: () => context.push('/profile/settings'),
                ),
                const Divider(height: 32),
                SizedBox(
                  width: double.infinity,
                  child: OutlinedButton.icon(
                    onPressed: () => _logout(context, ref),
                    icon: const Icon(Icons.logout),
                    label: const Text('Logout'),
                    style: OutlinedButton.styleFrom(
                      foregroundColor: Colors.red,
                      side: const BorderSide(color: Colors.red),
                      padding: const EdgeInsets.symmetric(vertical: 12),
                    ),
                  ),
                ),
              ],
            ),
          );
        },
      ),
    );
  }

  Future<void> _logout(BuildContext context, WidgetRef ref) async {
    await ref.read(authProvider.notifier).logout();
    if (context.mounted) {
      context.go('/login');
    }
  }
}

class _MenuItem extends StatelessWidget {
  final IconData icon;
  final String label;
  final VoidCallback onTap;

  const _MenuItem({required this.icon, required this.label, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return ListTile(
      leading: Icon(icon, color: Colors.green),
      title: Text(label),
      trailing: const Icon(Icons.chevron_right),
      onTap: onTap,
    );
  }
}
