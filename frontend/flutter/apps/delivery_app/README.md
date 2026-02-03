# delivery_app

LocalGrocery Delivery Partner app (Flutter).

## Mapbox (optional)

For the in-app delivery map (Android/iOS), set your Mapbox access token:

- **Option A:** Add to your env file (e.g. `frontend/flutter/.env.dev` or `apps/delivery_app/.env.dev`):
  ```
  MAPBOX_ACCESS_TOKEN=your_mapbox_secret_token_here
  ```
- **Option B:** Run with dart-define: `flutter run --dart-define=ACCESS_TOKEN=your_token`

## Deep links

Open a delivery by ID from outside the app:

- **Android/iOS:** `localgrocery://delivery/<delivery_id>` (e.g. `localgrocery://delivery/abc-123-uuid`)

## Getting Started

This project is a starting point for a Flutter application.

A few resources to get you started if this is your first Flutter project:

- [Lab: Write your first Flutter app](https://docs.flutter.dev/get-started/codelab)
- [Cookbook: Useful Flutter samples](https://docs.flutter.dev/cookbook)

For help getting started with Flutter development, view the
[online documentation](https://docs.flutter.dev/), which offers tutorials,
samples, guidance on mobile development, and a full API reference.
