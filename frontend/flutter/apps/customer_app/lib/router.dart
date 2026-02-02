import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'screens/splash/splash_screen.dart';
import 'screens/auth/login_screen.dart';
import 'screens/auth/otp_screen.dart';
import 'screens/home/home_screen.dart';
import 'screens/cart/cart_screen.dart';
import 'screens/checkout/checkout_screen.dart';
import 'screens/address/address_list_screen.dart';
import 'screens/address/add_address_screen.dart';
import 'screens/orders/orders_screen.dart';
import 'screens/orders/order_details_screen.dart';
import 'screens/orders/order_tracking_screen.dart';
import 'screens/orders/rate_order_screen.dart';
import 'screens/placeholder_screens.dart';
import 'screens/profile/profile_screen.dart';
import 'screens/profile/settings_screen.dart';
import 'screens/profile/wallet_screen.dart';
import 'screens/search/search_screen.dart';
import 'providers/auth_provider.dart';

/// Router configuration
final routerProvider = Provider<GoRouter>((ref) {
  final authState = ref.watch(authProvider);

  return GoRouter(
    initialLocation: '/home', // Skip auth, go directly to home
    redirect: (context, state) {
      // Disable authentication for development
      // TODO: Re-enable authentication before production
      return null;
      
      /* Original auth logic (commented out for development):
      final isLoggedIn = authState.value != null;
      final isLoggingIn = state.matchedLocation == '/login' || 
                          state.matchedLocation == '/otp';
      final isSplash = state.matchedLocation == '/';

      // Allow splash screen
      if (isSplash) return null;

      // If not logged in and not on login/otp, redirect to login
      if (!isLoggedIn && !isLoggingIn) {
        return '/login';
      }

      // If logged in and on login/otp, redirect to home
      if (isLoggedIn && isLoggingIn) {
        return '/home';
      }

      return null;
      */
    },
    routes: [
      GoRoute(
        path: '/',
        builder: (context, state) => const SplashScreen(),
      ),
      GoRoute(
        path: '/login',
        builder: (context, state) => const LoginScreen(),
      ),
      GoRoute(
        path: '/otp',
        builder: (context, state) {
          final phoneNumber = state.uri.queryParameters['phone'] ?? '';
          return OTPScreen(phoneNumber: phoneNumber);
        },
      ),
      GoRoute(
        path: '/home',
        builder: (context, state) => const HomeScreen(),
      ),
      GoRoute(
        path: '/search',
        builder: (context, state) {
          final q = state.uri.queryParameters['q'] ?? '';
          return SearchScreen(initialQuery: q);
        },
      ),
      GoRoute(
        path: '/product/:id',
        builder: (context, state) {
          final productId = state.pathParameters['id']!;
          return ProductDetailsScreen(productId: productId);
        },
      ),
      GoRoute(
        path: '/cart',
        builder: (context, state) => const CartScreen(),
      ),
      GoRoute(
        path: '/checkout',
        builder: (context, state) => const CheckoutScreen(),
      ),
      GoRoute(
        path: '/addresses',
        builder: (context, state) => const AddressListScreen(),
      ),
      GoRoute(
        path: '/addresses/add',
        builder: (context, state) => const AddAddressScreen(),
      ),
      GoRoute(
        path: '/orders',
        builder: (context, state) => const OrdersScreen(),
      ),
      GoRoute(
        path: '/orders/:id',
        builder: (context, state) {
          final orderId = state.pathParameters['id']!;
          return OrderDetailsScreen(orderId: orderId);
        },
      ),
      GoRoute(
        path: '/orders/:id/track',
        builder: (context, state) {
          final orderId = state.pathParameters['id']!;
          return OrderTrackingScreen(orderId: orderId);
        },
      ),
      GoRoute(
        path: '/orders/:id/rate',
        builder: (context, state) {
          final orderId = state.pathParameters['id']!;
          return RateOrderScreen(orderId: orderId);
        },
      ),
      GoRoute(
        path: '/profile',
        builder: (context, state) => const ProfileScreen(),
      ),
      GoRoute(
        path: '/profile/settings',
        builder: (context, state) => const SettingsScreen(),
      ),
      GoRoute(
        path: '/profile/wallet',
        builder: (context, state) => const WalletScreen(),
      ),
    ],
    errorBuilder: (context, state) => Scaffold(
      body: Center(
        child: Text('Page not found: ${state.uri.path}'),
      ),
    ),
  );
});
