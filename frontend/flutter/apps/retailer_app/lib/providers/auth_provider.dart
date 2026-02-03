import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:models/models.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:flutter/foundation.dart';
import 'package:core/core.dart';
import 'api_providers.dart';

class AuthNotifier extends AutoDisposeAsyncNotifier<User?> {
  late FlutterSecureStorage _secureStorage;

  @override
  Future<User?> build() async {
    _secureStorage = const FlutterSecureStorage();
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
          await logout();
        }
      }
    } catch (_) {
      debugPrint('Secure storage unavailable');
    }
    return null;
  }

  Future<bool> sendOTP(String phoneNumber) async {
    try {
      final authService = ref.read(authServiceProvider);
      final response = await authService.sendOTP(phoneNumber);
      return response.success;
    } catch (e) {
      debugPrint('SendOTP exception: $e');
      return false;
    }
  }

  Future<String?> verifyOTP(String phoneNumber, String otp) async {
    try {
      final authService = ref.read(authServiceProvider);
      final response = await authService.verifyOTP(
        phoneNumber: phoneNumber,
        otp: otp,
      );
      if (response.success && response.data != null) {
        await _secureStorage.write(
          key: AppConstants.keyAccessToken,
          value: response.data!.accessToken,
        );
        await _secureStorage.write(
          key: AppConstants.keyRefreshToken,
          value: response.data!.refreshToken,
        );
        state = AsyncValue.data(response.data!.user);
        return null;
      }
      return response.message ?? 'Verification failed';
    } catch (e) {
      return e.toString();
    }
  }

  Future<void> logout() async {
    try {
      final authService = ref.read(authServiceProvider);
      await authService.logout();
    } catch (_) {}
    await _secureStorage.delete(key: AppConstants.keyAccessToken);
    await _secureStorage.delete(key: AppConstants.keyRefreshToken);
    state = const AsyncValue.data(null);
  }

  Future<String?> getAccessToken() async {
    return _secureStorage.read(key: AppConstants.keyAccessToken);
  }

  bool get isLoggedIn => state.value != null;
}

final authProvider =
    AutoDisposeAsyncNotifierProvider<AuthNotifier, User?>(AuthNotifier.new);
