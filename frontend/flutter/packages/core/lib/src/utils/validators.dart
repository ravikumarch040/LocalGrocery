/// Input validation utilities
class Validators {
  Validators._();

  /// Validate phone number (Indian format: 10 digits or +91XXXXXXXXXX)
  static String? validatePhone(String? value) {
    if (value == null || value.isEmpty) {
      return 'Phone number is required';
    }
    
    final cleaned = value.replaceAll(RegExp(r'[^\d+]'), '');
    
    // Accept: 10 digit number starting with 6-9, or +91 followed by 10 digits
    final phoneRegex = RegExp(r'^(\+91)?[6-9]\d{9}$');
    if (!phoneRegex.hasMatch(cleaned)) {
      return 'Please enter a valid Indian phone number (10 digits or +91XXXXXXXXXX)';
    }
    
    return null;
  }

  /// Validate OTP (6 digits)
  static String? validateOtp(String? value) {
    if (value == null || value.isEmpty) {
      return 'OTP is required';
    }
    
    if (value.length != 6) {
      return 'OTP must be 6 digits';
    }
    
    final otpRegex = RegExp(r'^\d{6}$');
    if (!otpRegex.hasMatch(value)) {
      return 'Please enter a valid 6-digit OTP';
    }
    
    return null;
  }

  /// Validate OTP (6 digits) - alias for validateOtp
  static String? validateOTP(String? value) => validateOtp(value);

  /// Validate email
  static String? validateEmail(String? value) {
    if (value == null || value.isEmpty) {
      return 'Email is required';
    }
    
    final emailRegex = RegExp(
      r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
    );
    if (!emailRegex.hasMatch(value)) {
      return 'Please enter a valid email address';
    }
    
    return null;
  }

  /// Validate name
  static String? validateName(String? value) {
    if (value == null || value.isEmpty) {
      return 'Name is required';
    }
    
    if (value.length < 2) {
      return 'Name must be at least 2 characters';
    }
    
    if (value.length > 50) {
      return 'Name must be less than 50 characters';
    }
    
    return null;
  }

  /// Validate GST number
  static String? validateGst(String? value) {
    if (value == null || value.isEmpty) {
      return 'GST number is required';
    }
    
    final gstRegex = RegExp(
      r'^\d{2}[A-Z]{5}\d{4}[A-Z]{1}[A-Z\d]{1}[Z]{1}[A-Z\d]{1}$',
    );
    if (!gstRegex.hasMatch(value)) {
      return 'Please enter a valid GST number';
    }
    
    return null;
  }

  /// Validate PAN number
  static String? validatePan(String? value) {
    if (value == null || value.isEmpty) {
      return 'PAN number is required';
    }
    
    final panRegex = RegExp(r'^[A-Z]{5}\d{4}[A-Z]{1}$');
    if (!panRegex.hasMatch(value)) {
      return 'Please enter a valid PAN number';
    }
    
    return null;
  }

  /// Validate pincode (6 digits)
  static String? validatePincode(String? value) {
    if (value == null || value.isEmpty) {
      return 'Pincode is required';
    }
    
    final pincodeRegex = RegExp(r'^\d{6}$');
    if (!pincodeRegex.hasMatch(value)) {
      return 'Please enter a valid 6-digit pincode';
    }
    
    return null;
  }

  /// Validate IFSC code
  static String? validateIfsc(String? value) {
    if (value == null || value.isEmpty) {
      return 'IFSC code is required';
    }
    
    final ifscRegex = RegExp(r'^[A-Z]{4}0[A-Z0-9]{6}$');
    if (!ifscRegex.hasMatch(value)) {
      return 'Please enter a valid IFSC code';
    }
    
    return null;
  }

  /// Validate price/amount
  static String? validateAmount(String? value) {
    if (value == null || value.isEmpty) {
      return 'Amount is required';
    }
    
    final amount = double.tryParse(value);
    if (amount == null || amount <= 0) {
      return 'Please enter a valid amount';
    }
    
    return null;
  }

  /// Validate required field
  static String? validateRequired(String? value, [String fieldName = 'This field']) {
    if (value == null || value.trim().isEmpty) {
      return '$fieldName is required';
    }
    return null;
  }
}
