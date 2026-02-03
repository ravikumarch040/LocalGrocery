import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:app_links/app_links.dart';
import 'screens/splash/splash_screen.dart';
import 'screens/auth/login_screen.dart';
import 'screens/auth/otp_screen.dart';
import 'screens/home/home_screen.dart';
import 'screens/delivery/delivery_details_screen.dart';
import 'screens/delivery/delivery_map_screen.dart';
import 'screens/earnings/earnings_screen.dart';
import 'screens/profile/profile_screen.dart';

/// Initial path from deep link (e.g. localgrocery://delivery/123 -> /delivery/123). Set in main().
final initialDeepLinkPathProvider = Provider<String?>((ref) => null);

/// Builds path from app_links Uri. localgrocery://delivery/123 -> /delivery/123
String? pathFromDeepLinkUri(Uri? uri) {
  if (uri == null) return null;
  final path = uri.path;
  final host = uri.host;
  // localgrocery://delivery/123 => host=delivery, path=/123 -> /delivery/123
  if (host.isNotEmpty && path.isNotEmpty && path != '/') {
    final segment = path.startsWith('/') ? path.substring(1) : path;
    return '/$host/$segment';
  }
  if (host.isNotEmpty) return '/$host';
  if (path.isNotEmpty && path != '/') return path.startsWith('/') ? path : '/$path';
  return null;
}

final routerProvider = Provider<GoRouter>((ref) {
  final initialPath = ref.watch(initialDeepLinkPathProvider);
  final goRouter = GoRouter(
    initialLocation: initialPath ?? '/home',
    redirect: (context, state) => null,
    routes: [
      GoRoute(path: '/', builder: (context, state) => const SplashScreen()),
      GoRoute(path: '/login', builder: (context, state) => const LoginScreen()),
      GoRoute(
        path: '/otp',
        builder: (context, state) {
          final phone = state.uri.queryParameters['phone'] ?? '';
          return OTPScreen(phoneNumber: phone);
        },
      ),
      GoRoute(path: '/home', builder: (context, state) => const HomeScreen()),
      GoRoute(
        path: '/delivery/:id',
        builder: (context, state) {
          final id = state.pathParameters['id']!;
          return DeliveryDetailsScreen(deliveryId: id);
        },
        routes: [
          GoRoute(
            path: 'map',
            builder: (context, state) {
              final id = state.pathParameters['id']!;
              return DeliveryMapScreen(deliveryId: id);
            },
          ),
        ],
      ),
      GoRoute(path: '/earnings', builder: (context, state) => const EarningsScreen()),
      GoRoute(path: '/profile', builder: (context, state) => const ProfileScreen()),
    ],
    errorBuilder: (context, state) => Scaffold(
      body: Center(child: Text('Page not found: ${state.uri.path}')),
    ),
  );
  return goRouter;
});
