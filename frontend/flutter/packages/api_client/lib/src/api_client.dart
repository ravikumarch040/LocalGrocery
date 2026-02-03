import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:core/core.dart';

/// Base API client for making HTTP requests
class ApiClient {
  final String baseUrl;
  final Map<String, String> defaultHeaders;
  String? _accessToken;

  ApiClient({
    required this.baseUrl,
    this.defaultHeaders = const {},
  });

  /// Set access token for authenticated requests
  void setAccessToken(String? token) {
    _accessToken = token;
  }

  /// Get headers with authentication
  Map<String, String> _getHeaders({Map<String, String>? additionalHeaders}) {
    final headers = <String, String>{
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      ...defaultHeaders,
    };

    if (_accessToken != null) {
      headers['Authorization'] = 'Bearer $_accessToken';
    }

    if (additionalHeaders != null) {
      headers.addAll(additionalHeaders);
    }

    return headers;
  }

  /// Handle API response
  ApiResponse<T> _handleResponse<T>(
    http.Response response,
    T Function(dynamic)? fromJson,
  ) {
    final statusCode = response.statusCode;
    final body = response.body;

    try {
      final dynamic jsonData = jsonDecode(body);

      if (statusCode >= 200 && statusCode < 300) {
        // Handle both Map and List responses
        if (jsonData is Map<String, dynamic>) {
          return ApiResponse<T>.success(
            data: fromJson != null ? fromJson(jsonData['data'] ?? jsonData) : null,
            message: jsonData['message'] as String?,
            statusCode: statusCode,
          );
        } else {
          // For direct List responses (like categories endpoint)
          return ApiResponse<T>.success(
            data: fromJson != null ? fromJson(jsonData) : null,
            message: null,
            statusCode: statusCode,
          );
        }
      } else {
        final errorMap = jsonData is Map<String, dynamic> ? jsonData : {};
        return ApiResponse<T>.error(
          message: errorMap['message'] as String? ?? 'Request failed',
          errorCode: errorMap['error']?['code'] as String?,
          statusCode: statusCode,
        );
      }
    } catch (e) {
      return ApiResponse<T>.error(
        message: 'Failed to parse response: $e',
        statusCode: statusCode,
      );
    }
  }

  /// GET request
  Future<ApiResponse<T>> get<T>(
    String endpoint, {
    Map<String, String>? headers,
    Map<String, dynamic>? queryParams,
    T Function(dynamic)? fromJson,
  }) async {
    try {
      var uri = Uri.parse('$baseUrl$endpoint');
      if (queryParams != null) {
        uri = uri.replace(queryParameters: queryParams);
      }

      final response = await http
          .get(uri, headers: _getHeaders(additionalHeaders: headers))
          .timeout(AppConstants.apiTimeout);

      return _handleResponse(response, fromJson);
    } catch (e) {
      return ApiResponse<T>.error(message: _handleException(e));
    }
  }

  /// POST request
  Future<ApiResponse<T>> post<T>(
    String endpoint, {
    Map<String, dynamic>? body,
    Map<String, String>? headers,
    T Function(dynamic)? fromJson,
  }) async {
    try {
      final uri = Uri.parse('$baseUrl$endpoint');
      final response = await http
          .post(
            uri,
            headers: _getHeaders(additionalHeaders: headers),
            body: body != null ? jsonEncode(body) : null,
          )
          .timeout(AppConstants.apiTimeout);

      return _handleResponse(response, fromJson);
    } catch (e) {
      return ApiResponse<T>.error(message: _handleException(e));
    }
  }

  /// PUT request
  Future<ApiResponse<T>> put<T>(
    String endpoint, {
    Map<String, dynamic>? body,
    Map<String, String>? headers,
    T Function(dynamic)? fromJson,
  }) async {
    try {
      final uri = Uri.parse('$baseUrl$endpoint');
      final response = await http
          .put(
            uri,
            headers: _getHeaders(additionalHeaders: headers),
            body: body != null ? jsonEncode(body) : null,
          )
          .timeout(AppConstants.apiTimeout);

      return _handleResponse(response, fromJson);
    } catch (e) {
      return ApiResponse<T>.error(message: _handleException(e));
    }
  }

  /// PATCH request
  Future<ApiResponse<T>> patch<T>(
    String endpoint, {
    Map<String, dynamic>? body,
    Map<String, String>? headers,
    T Function(dynamic)? fromJson,
  }) async {
    try {
      final uri = Uri.parse('$baseUrl$endpoint');
      final response = await http
          .patch(
            uri,
            headers: _getHeaders(additionalHeaders: headers),
            body: body != null ? jsonEncode(body) : null,
          )
          .timeout(AppConstants.apiTimeout);

      return _handleResponse(response, fromJson);
    } catch (e) {
      return ApiResponse<T>.error(message: _handleException(e));
    }
  }

  /// DELETE request
  Future<ApiResponse<T>> delete<T>(
    String endpoint, {
    Map<String, String>? headers,
    T Function(dynamic)? fromJson,
  }) async {
    try {
      final uri = Uri.parse('$baseUrl$endpoint');
      final response = await http
          .delete(uri, headers: _getHeaders(additionalHeaders: headers))
          .timeout(AppConstants.apiTimeout);

      return _handleResponse(response, fromJson);
    } catch (e) {
      return ApiResponse<T>.error(message: _handleException(e));
    }
  }

  /// Handle exceptions
  String _handleException(dynamic error) {
    if (error.toString().contains('SocketException')) {
      return AppConstants.networkErrorMessage;
    } else if (error.toString().contains('TimeoutException')) {
      return 'Request timeout. Please try again.';
    } else {
      return AppConstants.genericErrorMessage;
    }
  }
}

/// API Response wrapper
class ApiResponse<T> {
  final bool success;
  final T? data;
  final String? message;
  final String? errorCode;
  final int? statusCode;

  ApiResponse({
    required this.success,
    this.data,
    this.message,
    this.errorCode,
    this.statusCode,
  });

  factory ApiResponse.success({
    T? data,
    String? message,
    int? statusCode,
  }) {
    return ApiResponse<T>(
      success: true,
      data: data,
      message: message,
      statusCode: statusCode,
    );
  }

  factory ApiResponse.error({
    required String message,
    String? errorCode,
    int? statusCode,
  }) {
    return ApiResponse<T>(
      success: false,
      message: message,
      errorCode: errorCode,
      statusCode: statusCode,
    );
  }

  bool get isUnauthorized => statusCode == 401;
  bool get isServerError => statusCode != null && statusCode! >= 500;
}
