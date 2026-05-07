import 'dart:async';

import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_crashlytics/firebase_crashlytics.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter/foundation.dart';

/// Centralized Firebase initialization for LocalGrocery apps.
/// Call [initializeFirebase] from main() after WidgetsFlutterBinding.ensureInitialized().
/// Register a top-level background handler in your app (see FIREBASE_SETUP.md).
class FirebaseInit {
  static bool _initialized = false;

  /// Initialize Firebase Core, Crashlytics, and FCM.
  /// Pass [options] from your app's firebase_options.dart (e.g. DefaultFirebaseOptions.currentPlatform).
  static Future<void> initializeFirebase(FirebaseOptions options) async {
    if (_initialized) return;
    await Firebase.initializeApp(options: options);
    _initialized = true;

    // Crashlytics: pass Flutter framework errors to Firebase
    FlutterError.onError = (details) {
      FirebaseCrashlytics.instance.recordFlutterFatalError(details);
    };
    // Pass uncaught async errors (e.g. from runZonedGuarded in main)
    PlatformDispatcher.instance.onError = (error, stack) {
      FirebaseCrashlytics.instance.recordError(error, stack, fatal: true);
      return true;
    };

    // FCM: request permission on iOS
    await _requestNotificationPermissionIfNeeded();
  }

  static Future<void> _requestNotificationPermissionIfNeeded() async {
    final messaging = FirebaseMessaging.instance;
    final settings = await messaging.getNotificationSettings();
    if (settings.authorizationStatus == AuthorizationStatus.notDetermined) {
      await messaging.requestPermission(
        alert: true,
        badge: true,
        sound: true,
      );
    }
  }

  /// Get the FCM token to send to your backend for targeting this device.
  static Future<String?> getFCMToken() => FirebaseMessaging.instance.getToken();

  /// Stream of messages received while app is in foreground.
  static Stream<RemoteMessage> get onMessage => FirebaseMessaging.onMessage;

  /// Message that opened the app from a terminated state (e.g. user tapped notification).
  static Future<RemoteMessage?> get initialMessage =>
      FirebaseMessaging.instance.getInitialMessage();

  /// Message that opened the app from background (user tapped notification).
  static Stream<RemoteMessage> get onMessageOpenedApp =>
      FirebaseMessaging.onMessageOpenedApp;

  /// Call from main() after [initializeFirebase]. Use this to record non-fatal
  /// errors (e.g. API failures) to Crashlytics. No-op if Firebase was not initialized.
  static void recordError(
    Object error,
    StackTrace? stackTrace, {
    String? reason,
    bool fatal = false,
  }) {
    if (!_initialized) return;
    FirebaseCrashlytics.instance.recordError(
      error,
      stackTrace,
      reason: reason,
      fatal: fatal,
    );
  }

  /// Set a custom key for Crashlytics reports (e.g. user id, app variant). No-op if not initialized.
  static Future<void> setCrashlyticsKey(String key, Object value) async {
    if (!_initialized) return;
    await FirebaseCrashlytics.instance.setCustomKey(key, value.toString());
  }
}
