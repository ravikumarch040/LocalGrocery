import 'package:equatable/equatable.dart';

/// Base exception class for application errors
class AppException extends Equatable implements Exception {
  final String message;
  final int? statusCode;
  final String? errorCode;
  final dynamic originalError;
  final StackTrace? stackTrace;

  const AppException({
    required this.message,
    this.statusCode,
    this.errorCode,
    this.originalError,
    this.stackTrace,
  });

  @override
  List<Object?> get props => [message, statusCode, errorCode];

  @override
  String toString() {
    return 'AppException(message: $message, statusCode: $statusCode, errorCode: $errorCode)';
  }
}

/// Network-related exceptions
class NetworkException extends AppException {
  const NetworkException({
    required super.message,
    super.statusCode,
    super.errorCode,
    super.originalError,
    super.stackTrace,
  });
}

/// Authentication exceptions
class AuthException extends AppException {
  const AuthException({
    required super.message,
    super.statusCode,
    super.errorCode,
    super.originalError,
    super.stackTrace,
  });
}

/// Validation exceptions
class ValidationException extends AppException {
  const ValidationException({
    required super.message,
    super.statusCode,
    super.errorCode,
    super.originalError,
    super.stackTrace,
  });
}

/// Server exceptions
class ServerException extends AppException {
  const ServerException({
    required super.message,
    super.statusCode,
    super.errorCode,
    super.originalError,
    super.stackTrace,
  });
}

/// Cache exceptions
class CacheException extends AppException {
  const CacheException({
    required super.message,
    super.statusCode,
    super.errorCode,
    super.originalError,
    super.stackTrace,
  });
}

/// Payment exceptions
class PaymentException extends AppException {
  const PaymentException({
    required super.message,
    super.statusCode,
    super.errorCode,
    super.originalError,
    super.stackTrace,
  });
}
