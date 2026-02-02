# Flutter Development Quick Start

## Phase 1: Foundation Setup ✅ COMPLETED

### What's Been Created

1. **Project Structure**
   ```
   frontend/flutter/
   ├── packages/
   │   ├── core/              ✅ Core utilities, constants, config
   │   └── models/            ✅ Shared data models
   ├── apps/                  📝 To be created
   ├── melos.yaml            ✅ Monorepo configuration
   ├── setup.ps1             ✅ Setup automation script
   └── README.md             ✅ Documentation
   ```

2. **Core Package** - Completed
   - Constants (API endpoints, app constants)
   - Environment configuration
   - Error handling (AppException, ErrorHandler)
   - Logging utilities
   - Validators (phone, OTP, email, GST, PAN, etc.)
   - Date/time utilities
   - Currency formatting

3. **Models Package** - Foundation
   - User model
   - Auth request/response models
   - API response wrapper
   - JSON serialization setup

### Next Immediate Steps

1. **Run Setup Script**
   ```powershell
   cd frontend/flutter
   .\setup.ps1
   ```

   This will:
   - Verify Flutter installation
   - Create remaining directories
   - Install dependencies
   - Create .env template files

2. **Create Flutter Apps**
   ```powershell
   cd apps
   
   # Customer App
   flutter create customer_app --org com.localgrocery --platforms android,ios
   
   # Retailer App
   flutter create retailer_app --org com.localgrocery --platforms android,ios
   
   # Delivery App
   flutter create delivery_app --org com.localgrocery --platforms android,ios
   ```

3. **Generate Model Code**
   ```powershell
   cd packages/models
   flutter pub run build_runner build --delete-conflicting-outputs
   ```

4. **Test Setup**
   ```powershell
   # Test core package
   cd packages/core
   flutter test
   
   # Test models package
   cd ../models
   flutter test
   ```

## Phase 2: Create Remaining Packages (Next 1-2 days)

### API Client Package
Create HTTP client with Dio + Retrofit for backend communication.

**Files to Create:**
```
packages/api_client/
├── lib/
│   ├── api_client.dart
│   ├── src/
│   │   ├── client/
│   │   │   ├── dio_client.dart
│   │   │   └── interceptors/
│   │   │       ├── auth_interceptor.dart
│   │   │       └── logging_interceptor.dart
│   │   └── services/
│   │       ├── auth_service.dart
│   │       ├── catalog_service.dart
│   │       ├── cart_service.dart
│   │       ├── order_service.dart
│   │       └── payment_service.dart
│   └── pubspec.yaml
```

### UI Components Package
Shared widgets and theme system.

**Files to Create:**
```
packages/ui_components/
├── lib/
│   ├── ui_components.dart
│   ├── src/
│   │   ├── theme/
│   │   │   ├── app_theme.dart
│   │   │   ├── colors.dart
│   │   │   └── typography.dart
│   │   ├── widgets/
│   │   │   ├── buttons/
│   │   │   ├── inputs/
│   │   │   ├── cards/
│   │   │   └── loading/
│   │   └── constants/
│   │       └── ui_constants.dart
│   └── pubspec.yaml
```

### Local Storage Package
Hive + SQLite + Secure Storage wrappers.

**Files to Create:**
```
packages/local_storage/
├── lib/
│   ├── local_storage.dart
│   ├── src/
│   │   ├── cache/
│   │   │   └── hive_manager.dart
│   │   ├── database/
│   │   │   └── sqlite_manager.dart
│   │   └── secure/
│   │       └── secure_storage_manager.dart
│   └── pubspec.yaml
```

## Phase 3: Customer App Implementation (Week 2-3)

### Authentication Module
1. Splash screen
2. Phone input screen
3. OTP verification screen
4. Location permission screen

### Home & Browse Module
1. Home screen with bottom navigation
2. Category listing
3. Store listing
4. Product listing
5. Product detail
6. Search functionality

### Cart & Checkout Module
1. Cart screen
2. Checkout flow
3. Address management
4. Payment integration

### Orders Module
1. Order tracking
2. Order history
3. Order details

## Development Commands Reference

### Melos Commands (Monorepo Management)
```powershell
# Bootstrap all packages (install dependencies)
melos bootstrap

# Run command in all packages
melos run analyze
melos run test
melos run format

# Clean all packages
melos clean
```

### Individual Package Commands
```powershell
# Get dependencies
flutter pub get

# Run code generation
flutter pub run build_runner build --delete-conflicting-outputs

# Watch mode (auto-regenerate)
flutter pub run build_runner watch

# Run tests
flutter test

# Analyze code
flutter analyze
```

### App Commands
```powershell
# Run app in debug mode
flutter run

# Run with specific device
flutter run -d <device-id>

# Build APK
flutter build apk --debug

# Build for release
flutter build apk --release
flutter build appbundle --release
```

## Environment Setup Checklist

- [ ] Flutter SDK installed (3.16.0+)
- [ ] Android Studio / VS Code with Flutter extensions
- [ ] Xcode (for iOS, macOS only)
- [ ] Android emulator or physical device
- [ ] Backend services running locally
- [ ] Environment variables configured (.env files)
- [ ] Git configured for monorepo

## Troubleshooting

### Common Issues

1. **"flutter: command not found"**
   - Add Flutter to PATH
   - Restart terminal/IDE

2. **"Melos not found"**
   ```powershell
   dart pub global activate melos
   # Add to PATH: %USERPROFILE%\AppData\Local\Pub\Cache\bin
   ```

3. **Code generation fails**
   ```powershell
   flutter pub get
   flutter clean
   flutter pub run build_runner build --delete-conflicting-outputs
   ```

4. **Hot reload not working**
   - Restart app with `R` in terminal
   - Full restart with `Ctrl+C` and `flutter run`

## Resources

- [Flutter Documentation](https://flutter.dev/docs)
- [Riverpod Guide](https://riverpod.dev/docs/introduction/getting_started)
- [Dio HTTP Client](https://pub.dev/packages/dio)
- [Go Router](https://pub.dev/packages/go_router)
- [Backend API Docs](../../backend/openapi.yaml)

## Current Status

✅ **Completed:**
- Implementation plan created
- Monorepo structure defined
- Core package implemented
- Models package foundation created
- Setup automation script ready
- Documentation prepared

📝 **Next Actions:**
1. Run setup script
2. Create Flutter apps
3. Implement remaining packages (api_client, ui_components, local_storage)
4. Start customer app authentication module

**Progress:** ~15% (Foundation Complete)
**Estimated Time to MVP:** 8-10 weeks
