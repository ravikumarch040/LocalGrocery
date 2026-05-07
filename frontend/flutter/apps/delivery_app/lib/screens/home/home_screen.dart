import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:core/core.dart';
import '../../providers/partner_provider.dart';
import '../../providers/delivery_provider.dart';
import '../../providers/api_providers.dart';

class HomeScreen extends ConsumerStatefulWidget {
  const HomeScreen({super.key});

  @override
  ConsumerState<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends ConsumerState<HomeScreen> with SingleTickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final partnerAsync = ref.watch(deliveryPartnerProvider);
    final isOnline = partnerAsync.value?.status == 'AVAILABLE';

    return Scaffold(
      appBar: AppBar(
        title: const Text('Deliveries'),
        actions: [
          partnerAsync.when(
            data: (partner) {
              if (partner == null) return const SizedBox.shrink();
              return Padding(
                padding: const EdgeInsets.only(right: 8, top: 12),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text(isOnline ? 'Online' : 'Offline', style: Theme.of(context).textTheme.bodySmall),
                    Switch(
                      value: isOnline,
                      onChanged: (v) => _setStatus(v ? 'AVAILABLE' : 'OFFLINE'),
                    ),
                  ],
                ),
              );
            },
            loading: () => const SizedBox.shrink(),
            error: (e, st) => const SizedBox.shrink(),
          ),
          IconButton(icon: const Icon(Icons.person), onPressed: () => context.push('/profile')),
        ],
        bottom: TabBar(
          controller: _tabController,
          tabs: const [
            Tab(text: 'Available'),
            Tab(text: 'My deliveries'),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          _AvailableList(onAccept: _acceptDelivery),
          _MyDeliveriesList(),
        ],
      ),
    );
  }

  Future<void> _setStatus(String status) async {
    final partnerId = await ref.read(deliveryPartnerIdProvider.future);
    if (partnerId == null) return;
    final service = ref.read(deliveryServiceProvider);
    final res = await service.updatePartnerStatus(partnerId: partnerId, status: status);
    if (res.success) ref.invalidate(deliveryPartnerProvider);
  }

  Future<void> _acceptDelivery(String deliveryId) async {
    final partnerId = await ref.read(deliveryPartnerIdProvider.future);
    if (partnerId == null) {
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Partner ID not set')));
      return;
    }
    final service = ref.read(deliveryServiceProvider);
    final res = await service.assignDelivery(deliveryId: deliveryId, deliveryPartnerId: partnerId);
    if (!mounted) return;
    if (res.success) {
      ref.invalidate(availableDeliveriesProvider);
      ref.invalidate(myDeliveriesProvider);
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Delivery accepted')));
      context.push('/delivery/$deliveryId');
    } else {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(res.message ?? 'Failed'), backgroundColor: Colors.red));
    }
  }
}

class _AvailableList extends ConsumerWidget {
  final void Function(String deliveryId) onAccept;

  const _AvailableList({required this.onAccept});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final async = ref.watch(availableDeliveriesProvider);

    return async.when(
      data: (list) {
        if (list.isEmpty) {
          return Center(child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(Icons.inbox_outlined, size: 64, color: Colors.grey.shade400),
              const SizedBox(height: 16),
              Text('No available deliveries', style: Theme.of(context).textTheme.titleMedium?.copyWith(color: Colors.grey.shade600)),
            ],
          ));
        }
        return RefreshIndicator(
          onRefresh: () async => ref.invalidate(availableDeliveriesProvider),
          child: ListView.builder(
            padding: const EdgeInsets.all(16),
            itemCount: list.length,
            itemBuilder: (context, index) {
              final d = list[index];
              return Card(
                margin: const EdgeInsets.only(bottom: 12),
                child: ListTile(
                  title: Text(d.pickupAddress),
                  subtitle: Text('${d.deliveryAddress}\n${d.distanceKm != null ? "${d.distanceKm!.toStringAsFixed(1)} km" : ""} · ₹${d.deliveryFee?.toStringAsFixed(0) ?? "—"}'),
                  trailing: FilledButton(
                    onPressed: () => onAccept(d.id),
                    child: const Text('Accept'),
                  ),
                  onTap: () => context.push('/delivery/${d.id}'),
                ),
              );
            },
          ),
        );
      },
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (e, st) => AsyncErrorView(
        error: e,
        onRetry: () => ref.invalidate(availableDeliveriesProvider),
      ),
    );
  }
}

class _MyDeliveriesList extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final async = ref.watch(myDeliveriesProvider);

    return async.when(
      data: (list) {
        if (list.isEmpty) {
          return Center(child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(Icons.receipt_long_outlined, size: 64, color: Colors.grey.shade400),
              const SizedBox(height: 16),
              Text('No active deliveries', style: Theme.of(context).textTheme.titleMedium?.copyWith(color: Colors.grey.shade600)),
            ],
          ));
        }
        return RefreshIndicator(
          onRefresh: () async => ref.invalidate(myDeliveriesProvider),
          child: ListView.builder(
            padding: const EdgeInsets.all(16),
            itemCount: list.length,
            itemBuilder: (context, index) {
              final d = list[index];
              return Card(
                margin: const EdgeInsets.only(bottom: 12),
                child: ListTile(
                  title: Text(d.deliveryAddress),
                  subtitle: Text('${d.status} · ₹${d.deliveryFee?.toStringAsFixed(0) ?? "—"}'),
                  trailing: const Icon(Icons.chevron_right),
                  onTap: () => context.push('/delivery/${d.id}'),
                ),
              );
            },
          ),
        );
      },
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (e, st) => AsyncErrorView(
        error: e,
        onRetry: () => ref.invalidate(myDeliveriesProvider),
      ),
    );
  }
}
