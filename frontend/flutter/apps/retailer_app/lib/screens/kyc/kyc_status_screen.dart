import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../providers/store_provider.dart';

class KycStatusScreen extends ConsumerWidget {
  const KycStatusScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final storeAsync = ref.watch(retailerStoreProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('KYC Status')),
      body: storeAsync.when(
        data: (store) {
          final status = store?.kycStatus ?? 'PENDING';
          final isApproved = status.toUpperCase() == 'APPROVED';
          final isRejected = status.toUpperCase() == 'REJECTED';
          return SingleChildScrollView(
            padding: const EdgeInsets.all(24),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                const SizedBox(height: 24),
                Icon(
                  isApproved
                      ? Icons.check_circle
                      : isRejected
                          ? Icons.cancel
                          : Icons.pending_actions,
                  size: 80,
                  color: isApproved
                      ? Colors.green
                      : isRejected
                          ? Colors.red
                          : Colors.orange,
                ),
                const SizedBox(height: 24),
                Text(
                  status,
                  style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 8),
                Text(
                  isApproved
                      ? 'Your store is verified and live.'
                      : isRejected
                          ? 'Verification was rejected. Upload correct documents.'
                          : 'Complete KYC to go live and receive orders.',
                  style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                        color: Colors.grey.shade600,
                      ),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 32),
                if (!isApproved)
                  FilledButton.icon(
                    onPressed: () {
                      // TODO: Navigate to KYC form (business info, GST, bank, docs)
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(
                          content: Text('KYC form coming soon'),
                        ),
                      );
                    },
                    icon: const Icon(Icons.upload_file),
                    label: Text(isRejected ? 'Upload missing docs' : 'Complete KYC'),
                  ),
                const SizedBox(height: 24),
                Card(
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Required documents',
                          style: Theme.of(context).textTheme.titleMedium,
                        ),
                        const SizedBox(height: 12),
                        _DocItem(icon: Icons.badge, title: 'PAN card'),
                        _DocItem(icon: Icons.receipt_long, title: 'GST (optional)'),
                        _DocItem(icon: Icons.account_balance, title: 'Cancelled cheque'),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          );
        },
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => Center(child: Text('Error: $e')),
      ),
    );
  }
}

class _DocItem extends StatelessWidget {
  final IconData icon;
  final String title;

  const _DocItem({required this.icon, required this.title});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6),
      child: Row(
        children: [
          Icon(icon, size: 20, color: Colors.grey.shade600),
          const SizedBox(width: 12),
          Text(title),
        ],
      ),
    );
  }
}
