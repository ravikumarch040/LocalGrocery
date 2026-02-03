import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:fl_chart/fl_chart.dart';
import '../../providers/auth_provider.dart';
import '../../providers/order_provider.dart';
import '../../providers/store_provider.dart';

class DashboardScreen extends ConsumerWidget {
  const DashboardScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final storeAsync = ref.watch(retailerStoreProvider);
    final newOrdersAsync = ref.watch(retailerOrdersProvider('PLACED'));
    final analyticsAsync = ref.watch(retailerAnalyticsProvider);
    final auth = ref.watch(authProvider).value;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Dashboard'),
        actions: [
          IconButton(
            icon: const Icon(Icons.notifications_outlined),
            onPressed: () {},
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: () async {
          ref.invalidate(retailerStoreProvider);
          ref.invalidate(retailerOrdersProvider);
          ref.invalidate(retailerOrdersForAnalyticsProvider);
          ref.invalidate(retailerAnalyticsProvider);
        },
        child: SingleChildScrollView(
          physics: const AlwaysScrollableScrollPhysics(),
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Text(
                'Hello, ${auth?.name ?? auth?.phone ?? 'Retailer'}',
                style: Theme.of(context).textTheme.titleLarge,
              ),
              const SizedBox(height: 8),
              storeAsync.when(
                data: (store) => Text(
                  store?.name ?? 'Your store',
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                        color: Colors.grey.shade600,
                      ),
                ),
                loading: () => const SizedBox.shrink(),
                error: (e, st) => const SizedBox.shrink(),
              ),
              const SizedBox(height: 24),
              analyticsAsync.when(
                data: (a) => Row(
                  children: [
                    Expanded(
                      child: _StatCard(
                        title: "Today's orders",
                        value: '${a.todayOrderCount}',
                        icon: Icons.shopping_cart,
                        color: Colors.amber,
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: _StatCard(
                        title: "Today's revenue",
                        value: '₹${a.todayRevenue.toStringAsFixed(0)}',
                        icon: Icons.currency_rupee,
                        color: Colors.green,
                      ),
                    ),
                  ],
                ),
                loading: () => Row(
                  children: [
                    Expanded(child: _StatCard(title: "Today's orders", value: '…', icon: Icons.shopping_cart, color: Colors.amber)),
                    const SizedBox(width: 12),
                    Expanded(child: _StatCard(title: "Today's revenue", value: '…', icon: Icons.currency_rupee, color: Colors.green)),
                  ],
                ),
                error: (_, __) => Row(
                  children: [
                    Expanded(child: _StatCard(title: "Today's orders", value: '—', icon: Icons.shopping_cart, color: Colors.amber)),
                    const SizedBox(width: 12),
                    Expanded(child: _StatCard(title: "Today's revenue", value: '₹—', icon: Icons.currency_rupee, color: Colors.green)),
                  ],
                ),
              ),
              const SizedBox(height: 12),
              newOrdersAsync.when(
                data: (orders) => Card(
                  child: ListTile(
                    leading: const Icon(Icons.pending_actions, color: Colors.orange),
                    title: Text('${orders.length} new orders'),
                    subtitle: const Text('Accept or reject'),
                    trailing: const Icon(Icons.chevron_right),
                    onTap: () => context.go('/orders'),
                  ),
                ),
                loading: () => const Card(
                  child: ListTile(
                    leading: SizedBox(
                      width: 24,
                      height: 24,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    ),
                    title: Text('Loading new orders…'),
                  ),
                ),
                error: (e, st) => Card(
                  child: ListTile(
                    leading: const Icon(Icons.error_outline, color: Colors.red),
                    title: const Text('Could not load orders'),
                    subtitle: Text('$e'),
                  ),
                ),
              ),
              const SizedBox(height: 24),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    'Sales (last 7 days)',
                    style: Theme.of(context).textTheme.titleMedium,
                  ),
                  TextButton(
                    onPressed: () => context.push('/analytics'),
                    child: const Text('View all'),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              analyticsAsync.when(
                data: (a) => SizedBox(
                  height: 180,
                  child: _SalesBarChart(series: a.last7Days),
                ),
                loading: () => const SizedBox(height: 180, child: Center(child: CircularProgressIndicator())),
                error: (_, __) => const SizedBox(height: 180, child: Center(child: Text('Could not load chart'))),
              ),
              const SizedBox(height: 24),
              Row(
                children: [
                  Expanded(
                    child: OutlinedButton.icon(
                      onPressed: () => context.go('/inventory/add'),
                      icon: const Icon(Icons.add),
                      label: const Text('Add product'),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: OutlinedButton.icon(
                      onPressed: () => context.go('/orders'),
                      icon: const Icon(Icons.receipt_long),
                      label: const Text('View orders'),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _StatCard extends StatelessWidget {
  final String title;
  final String value;
  final IconData icon;
  final Color color;

  const _StatCard({
    required this.title,
    required this.value,
    required this.icon,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Icon(icon, color: color, size: 28),
            const SizedBox(height: 8),
            Text(
              title,
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: Colors.grey.shade600,
                  ),
            ),
            const SizedBox(height: 4),
            Text(
              value,
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
            ),
          ],
        ),
      ),
    );
  }
}

class _SalesBarChart extends StatelessWidget {
  final List<({int dayOffset, double revenue})> series;

  const _SalesBarChart({required this.series});

  @override
  Widget build(BuildContext context) {
    final maxY = series.isEmpty ? 100.0 : (series.map((e) => e.revenue).reduce((a, b) => a > b ? a : b) * 1.1).clamp(10.0, double.infinity);
    final now = DateTime.now();
    final dayLabels = List.generate(7, (i) {
      final d = now.subtract(Duration(days: 6 - i));
      const short = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
      return '${short[d.weekday - 1]}\n${d.day}';
    });

    return BarChart(
      BarChartData(
        alignment: BarChartAlignment.spaceAround,
        maxY: maxY,
        barTouchData: BarTouchData(enabled: false),
        titlesData: FlTitlesData(
          show: true,
          bottomTitles: AxisTitles(
            sideTitles: SideTitles(
              showTitles: true,
              getTitlesWidget: (value, meta) {
                final i = value.toInt();
                if (i >= 0 && i < dayLabels.length) {
                  return Padding(
                    padding: const EdgeInsets.only(top: 8),
                    child: Text(dayLabels[i], style: const TextStyle(fontSize: 9), textAlign: TextAlign.center),
                  );
                }
                return const Text('');
              },
              reservedSize: 32,
            ),
          ),
          leftTitles: AxisTitles(
            sideTitles: SideTitles(
              showTitles: true,
              reservedSize: 36,
              getTitlesWidget: (value, meta) => Text(
                value.toInt().toString(),
                style: const TextStyle(fontSize: 10),
              ),
            ),
          ),
          topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
          rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
        ),
        gridData: const FlGridData(show: false),
        borderData: FlBorderData(show: false),
        barGroups: List.generate(7, (i) {
          final rev = i < series.length ? series[i].revenue : 0.0;
          return BarChartGroupData(
            x: i,
            barRods: [
              BarChartRodData(
                toY: rev,
                color: Colors.amber.shade400,
                width: 16,
                borderRadius: const BorderRadius.vertical(top: Radius.circular(4)),
              ),
            ],
            showingTooltipIndicators: [0],
          );
        }),
      ),
    );
  }
}
