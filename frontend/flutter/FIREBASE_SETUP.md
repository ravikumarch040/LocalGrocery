# Firebase Setup (LocalGrocery Flutter Apps)

This document describes how to complete Firebase setup for **Customer App**, **Retailer App**, and **Delivery App**. The codebase already includes Firebase Core, FCM (Cloud Messaging), and Crashlytics; you only need to register the apps with Firebase and add config files.

## Prerequisites

- [Firebase CLI](https://firebase.google.com/docs/cli#setup_update_cli) installed
- [FlutterFire CLI](https://firebase.flutter.dev/docs/overview):  
  `dart pub global activate flutterfire_cli`
- Log in: `firebase login`

## 1. Configure each app with Firebase

From the **repository root**, run FlutterFire configure **for each app** (use one Firebase project for all three apps, or separate projects if you prefer):

```bash
# Customer App
cd frontend/flutter/apps/customer_app
flutterfire configure

# Retailer App
cd ../retailer_app
flutterfire configure

# Delivery App
cd ../delivery_app
flutterfire configure
```

For each app, `flutterfire configure` will:

- Let you select or create a Firebase project
- Register the app for Android and/or iOS
- Generate `lib/firebase_options.dart` (replacing the placeholder)
- **Android:** Download `android/app/google-services.json`
- **iOS:** Download `ios/Runner/GoogleService-Info.plist` (you may need to add it to the Xcode project if not automatic)

After this, the apps will build and Firebase (FCM + Crashlytics) will work.

## 2. What’s already implemented

- **Firebase Core** – Initialized in each app’s `main.dart` using `FirebaseInit.initializeFirebase(...)` from the `core` package.
- **FCM (Push notifications)**  
  - Background handler registered in each app’s `main.dart`.  
  - Use `FirebaseInit.getFCMToken()` to get the device token and send it to your backend.  
  - Use `FirebaseInit.onMessage` for foreground messages, `FirebaseInit.onMessageOpenedApp` and `FirebaseInit.initialMessage` for notification taps.
- **Crashlytics**  
  - Flutter errors and uncaught async errors are reported via `FirebaseInit` and `runZonedGuarded` in `main.dart`.  
  - Use `FirebaseInit.recordError(error, stack)` for non-fatal errors.  
  - Use `FirebaseInit.setCrashlyticsKey('key', value)` for custom keys.

## 3. Sending the FCM token to your backend

After login, get the token and POST it to your API (e.g. `/users/me/fcm-token`):

```dart
final token = await FirebaseInit.getFCMToken();
if (token != null) {
  await apiClient.updateFcmToken(token);
}
```

Listen for token refresh and update the backend again:

```dart
FirebaseMessaging.instance.onTokenRefresh.listen((newToken) {
  apiClient.updateFcmToken(newToken);
});
```

## 4. Android

- The **Google Services** plugin is applied in each app’s `android/app/build.gradle.kts`.
- `google-services.json` is required for release; `flutterfire configure` places it in `android/app/`.
- No extra manifest permissions are required for FCM beyond the plugin defaults.

## 5. iOS

- **Background Modes** `fetch` and `remote-notification` are set in each app’s `ios/Runner/Info.plist`.
- Push notifications require a valid **Apple Developer** provisioning profile and **Push Notifications** capability in Xcode.
- Add **Push Notifications** and optionally **Background Modes > Remote notifications** in Xcode for the Runner target.

## 6. Running without Firebase (e.g. local dev)

If `google-services.json` / `GoogleService-Info.plist` are missing or Firebase init fails, the apps catch the error and continue without Firebase; FCM and Crashlytics are simply inactive.

## 7. Optional: one Firebase project vs three

- **One project:** Create one Firebase project and register three apps (customer, retailer, delivery). Run `flutterfire configure` in each app directory and select the same project. Good for a single product with one backend.
- **Three projects:** Use a separate Firebase project per app if you need separate quotas, teams, or Analytics properties.
