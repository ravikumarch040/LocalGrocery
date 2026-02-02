import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:models/models.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:flutter/foundation.dart';
import 'api_providers.dart';
import 'package:core/core.dart';

part 'auth_provider.g.dart';

/// Authentication state provider
@riverpod
class Auth extends _$Auth {
  late FlutterSecureStorage _secureStorage;

  @override
  FutureOr<User?> build() async {
    // Initialize storage
    _secureStorage = const FlutterSecureStorage();

    // Try to load user from storage; ignore secure storage init issues on desktop
    try {
      final token = await _secureStorage.read(key: AppConstants.keyAccessToken);
      if (token != null) {
        try {
          final authService = ref.read(authServiceProvider);
          final response = await authService.getProfile();
          if (response.success && response.data != null) {
            return response.data;
          }
        } catch (e) {
          // Token invalid or expired, clear it
          await logout();
        }
      }
    } catch (_) {
      // Secure storage not available on this platform; continue without cached token
      debugPrint('Secure storage unavailable; continuing without cached token');
    }
    return null;
  }

  /// Send OTP to phone number
  Future<bool> sendOTP(String phoneNumber) async {
    try {
      final authService = ref.read(authServiceProvider);
      final response = await authService.sendOTP(phoneNumber);
      if (!response.success) {
        debugPrint('SendOTP error: ${response.message}');
      }
      return response.success;
    } catch (e) {
      debugPrint('SendOTP exception: $e');
      return false;
    }
  }

  /// Verify OTP and login
  Future<String?> verifyOTP(String phoneNumber, String otp) async {
    try {
      final authService = ref.read(authServiceProvider);
      final response = await authService.verifyOTP(
        phoneNumber: phoneNumber,
        otp: otp,
      );

      if (response.success && response.data != null) {
        // Save tokens
        await _secureStorage.write(
          key: AppConstants.keyAccessToken,
          value: response.data!.accessToken,
        );
        await _secureStorage.write(
          key: AppConstants.keyRefreshToken,
          value: response.data!.refreshToken,
        );

        // Update state
        state = AsyncValue.data(response.data!.user);
        return null; // Success
      }
      return response.message ?? 'Verification failed';
    } catch (e) {
      return e.toString();
    }
  }

  /// Logout
  Future<void> logout() async {
    try {
      final authService = ref.read(authServiceProvider);
      await authService.logout();
    } catch (e) {
      // Ignore logout errors
    } finally {
      // Clear tokens
      await _secureStorage.delete(key: AppConstants.keyAccessToken);
      await _secureStorage.delete(key: AppConstants.keyRefreshToken);
      
      // Clear state
      state = const AsyncValue.data(null);
    }
  }

  /// Get current access token
  Future<String?> getAccessToken() async {
    return await _secureStorage.read(key: AppConstants.keyAccessToken);
  }

  /// Check if user is logged in
  bool get isLoggedIn {
    return state.value != null;
  }
}
