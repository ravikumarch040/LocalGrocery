import 'package:api_client/src/api_client.dart' as api;
import 'package:models/models.dart' as models;

/// Authentication API service
class AuthService {
  final api.ApiClient _apiClient;

  AuthService(this._apiClient);

  /// Send OTP to phone number
  Future<api.ApiResponse<void>> sendOTP(String phoneNumber) async {
    // Normalize phone number: remove non-digits except +, ensure +91 format
    final normalized = _normalizePhoneNumber(phoneNumber);
    return await _apiClient.post(
      '/api/v1/auth/send-otp',
      body: {'phone': normalized},
    );
  }

  /// Verify OTP and get token
  Future<api.ApiResponse<models.AuthResponse>> verifyOTP({
    required String phoneNumber,
    required String otp,
  }) async {
    // Normalize phone number
    final normalized = _normalizePhoneNumber(phoneNumber);
    return await _apiClient.post(
      '/api/v1/auth/verify-otp',
      body: {
        'phone': normalized,
        'otp': otp,
      },
      fromJson: (json) => models.AuthResponse.fromJson(json),
    );
  }

  /// Refresh access token
  Future<api.ApiResponse<models.AuthResponse>> refreshToken(String refreshToken) async {
    return await _apiClient.post(
      '/api/v1/auth/refresh',
      body: {'refresh_token': refreshToken},
      fromJson: (json) => models.AuthResponse.fromJson(json),
    );
  }

  /// Get current user profile
  Future<api.ApiResponse<models.User>> getProfile() async {
    return await _apiClient.get(
      '/api/v1/auth/profile',
      fromJson: (json) => models.User.fromJson(json),
    );
  }

  /// Update user profile
  Future<api.ApiResponse<models.User>> updateProfile({
    String? name,
    String? email,
  }) async {
    return await _apiClient.put(
      '/api/v1/auth/profile',
      body: {
        if (name != null) 'name': name,
        if (email != null) 'email': email,
      },
      fromJson: (json) => models.User.fromJson(json),
    );
  }

  /// Register FCM token for push notifications
  Future<api.ApiResponse<void>> registerFCMToken(String fcmToken) async {
    return await _apiClient.post(
      '/api/v1/auth/fcm-token',
      body: {'fcm_token': fcmToken},
    );
  }

  /// Logout
  Future<api.ApiResponse<void>> logout() async {
    return await _apiClient.post('/api/v1/auth/logout');
  }

  /// Normalize phone number to +91 format
  String _normalizePhoneNumber(String phone) {
    // Remove all non-digit characters except +
    final cleaned = phone.replaceAll(RegExp(r'[^\d+]'), '');
    
    // If already has +91, return as is
    if (cleaned.startsWith('+91')) {
      return cleaned;
    }
    
    // If starts with 91, add +
    if (cleaned.startsWith('91')) {
      return '+${cleaned}';
    }
    
    // If just 10 digits, add +91
    if (cleaned.length == 10) {
      return '+91$cleaned';
    }
    
    // Return as is with + prefix if missing
    return cleaned.startsWith('+') ? cleaned : '+$cleaned';
  }
}

/// Auth response model
class AuthResponse {
  final String accessToken;
  final String refreshToken;
  final models.User user;

  AuthResponse({
    required this.accessToken,
    required this.refreshToken,
    required this.user,
  });

  factory AuthResponse.fromJson(Map<String, dynamic> json) {
    return AuthResponse(
      accessToken: json['access_token'] as String,
      refreshToken: json['refresh_token'] as String,
      user: models.User.fromJson(json['user'] as Map<String, dynamic>),
    );
  }
}
