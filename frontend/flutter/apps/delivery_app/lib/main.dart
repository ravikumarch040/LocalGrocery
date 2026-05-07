import 'dart:async';

import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:core/core.dart';
import 'package:mapbox_maps_flutter/mapbox_maps_flutter.dart';
import 'package:app_links/app_links.dart';
import 'firebase_options.dart';
import 'router.dart';

@pragma('vm:entry-point')
Future<void> _firebaseMessagingBackgroundHandler(RemoteMessage message) async {}

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await AppConfig.initialize(environment: 'dev');

  final token = AppConfig.mapboxAccessToken.isNotEmpty
      ? AppConfig.mapboxAccessToken
      : String.fromEnvironment('ACCESS_TOKEN', defaultValue: '');
  if (token.isNotEmpty) {
    MapboxOptions.setAccessToken(token);
  }

  try {
    await FirebaseInit.initializeFirebase(DefaultFirebaseOptions.currentPlatform);
    FirebaseMessaging.onBackgroundMessage(_firebaseMessagingBackgroundHandler);
  } catch (_) {}

  final appLinks = AppLinks();
  Uri? initialUri;
  try {
    initialUri = await appLinks.getInitialLink();
  } catch (_) {}
  final initialPath = pathFromDeepLinkUri(initialUri);

  runZonedGuarded(
    () => runApp(
      ProviderScope(
        overrides: [
          if (initialPath != null) initialDeepLinkPathProvider.overrideWithValue(initialPath),
        ],
        child: const DeliveryApp(),
      ),
    ),
    (error, stack) => FirebaseInit.recordError(error, stack),
  );
}

class DeliveryApp extends ConsumerStatefulWidget {
  const DeliveryApp({super.key});

  @override
  ConsumerState<DeliveryApp> createState() => _DeliveryAppState();
}

class _DeliveryAppState extends ConsumerState<DeliveryApp> {
  StreamSubscription<Uri>? _linkSub;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final router = ref.read(routerProvider);
      _linkSub = AppLinks().uriLinkStream.listen((uri) {
        final path = pathFromDeepLinkUri(uri);
        if (path != null) router.go(path);
      });
    });
  }

  @override
  void dispose() {
    _linkSub?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final router = ref.watch(routerProvider);

    return MaterialApp.router(
      title: 'LocalGrocery Delivery',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: Colors.blue,
          primary: Colors.blue.shade700,
          brightness: Brightness.light,
        ),
        useMaterial3: true,
        textTheme: GoogleFonts.poppinsTextTheme(),
        elevatedButtonTheme: ElevatedButtonThemeData(
          style: ElevatedButton.styleFrom(
            padding: const EdgeInsets.symmetric(vertical: 16),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
            ),
          ),
        ),
        inputDecorationTheme: InputDecorationTheme(
          border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
          filled: true,
          fillColor: Colors.grey[50],
        ),
      ),
      routerConfig: router,
    );
  }
}
