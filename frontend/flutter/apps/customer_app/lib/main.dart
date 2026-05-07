import 'dart:async';

import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:core/core.dart';
import 'firebase_options.dart';
import 'router.dart';

/// FCM background handler. Must be top-level. Runs when app is terminated or backgrounded.
@pragma('vm:entry-point')
Future<void> _firebaseMessagingBackgroundHandler(RemoteMessage message) async {
  // Optional: initialize Firebase in background isolate if not already done
  // Firebase.initializeApp() is typically only needed for background handler on Android
}

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  await AppConfig.initialize(environment: 'dev');

  // Firebase: init (run `flutterfire configure` in apps/customer_app to replace firebase_options)
  try {
    await FirebaseInit.initializeFirebase(DefaultFirebaseOptions.currentPlatform);
    FirebaseMessaging.onBackgroundMessage(_firebaseMessagingBackgroundHandler);
  } catch (_) {
    // App still runs if Firebase is not configured (e.g. missing google-services.json)
  }

  runZonedGuarded(
    () => runApp(
      const ProviderScope(
        child: MyApp(),
      ),
    ),
    (error, stack) => FirebaseInit.recordError(error, stack),
  );
}

class MyApp extends ConsumerWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final router = ref.watch(routerProvider);

    return MaterialApp.router(
      title: 'LocalGrocery',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: Colors.green,
          primary: Colors.green,
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
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(12),
          ),
          filled: true,
          fillColor: Colors.grey[50],
        ),
      ),
      routerConfig: router,
    );
  }
}
