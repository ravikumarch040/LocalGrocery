import 'app_exception.dart';
import '../utils/logger.dart';

/// Centralized error handler
class ErrorHandler {
  ErrorHandler._();

  /// Handle and convert errors to AppException
  static AppException handleError(dynamic error, [StackTrace? stackTrace]) {
    AppLogger.error('Error occurred', error, stackTrace);

    if (error is AppException) {
      return error;
    }

    // Default fallback
    return AppException(
      message: error.toString(),
      originalError: error,
      stackTrace: stackTrace,
    );
  }

  /// Get user-friendly error message
  static String getUserMessage(AppException exception) {
    // Handle specific error codes
    switch (exception.errorCode) {
      case 'AUTH_INVALID_OTP':
        return 'Invalid OTP. Please try again.';
      case 'AUTH_TOKEN_EXPIRED':
        return 'Your session has expired. Please login again.';
      case 'RETAILER_KYC_PENDING':
        return 'Your KYC verification is pending. Please complete it to continue.';
      case 'INVENTORY_OVERSOLD':
        return 'This item is currently out of stock.';
      case 'CART_PRICE_CHANGED':
        return 'Product price has changed. Please review your cart.';
      case 'PAYMENT_GATEWAY_TIMEOUT':
        return 'Payment gateway is currently unavailable. Please try again.';
      case 'PAYMENT_DECLINED':
        return 'Payment was declined. Please try a different payment method.';
      case 'ORDER_NOT_FOUND':
        return 'Order not found.';
      case 'STORE_OUTSIDE_DELIVERY_RADIUS':
        return 'This store does not deliver to your location.';
      case 'DELIVERY_PARTNER_UNAVAILABLE':
        return 'No delivery partners available at the moment.';
      case 'RATE_LIMIT_EXCEEDED':
        return 'Too many requests. Please wait a moment and try again.';
      default:
        return exception.message;
    }
  }

  /// Check if error is retryable
  static bool isRetryable(AppException exception) {
    const retryableCodes = [
      'PAYMENT_GATEWAY_TIMEOUT',
      'DELIVERY_PARTNER_UNAVAILABLE',
      'RATE_LIMIT_EXCEEDED',
      'DATABASE_TIMEOUT',
    ];

    return exception.errorCode != null &&
        retryableCodes.contains(exception.errorCode);
  }
}
