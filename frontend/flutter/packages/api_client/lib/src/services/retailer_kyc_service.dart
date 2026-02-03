import 'package:api_client/src/api_client.dart' as api;
import 'package:core/core.dart';

/// Request body for submitting retailer KYC (matches wiki: business info, type, docs).
class KycSubmitRequest {
  final String businessName;
  final String ownerName;
  final String phone;
  final String email;
  final KycAddress address;
  final String businessType; // Kirana, Supermarket, Pharmacy, Other
  final String deliveryPreference; // Self, Platform, Third-party
  final String? panDocumentBase64; // optional: base64 image
  final String? gstDocumentBase64;
  final String? cancelledChequeBase64;

  const KycSubmitRequest({
    required this.businessName,
    required this.ownerName,
    required this.phone,
    required this.email,
    required this.address,
    required this.businessType,
    required this.deliveryPreference,
    this.panDocumentBase64,
    this.gstDocumentBase64,
    this.cancelledChequeBase64,
  });

  Map<String, dynamic> toJson() => {
        'business_name': businessName,
        'owner_name': ownerName,
        'phone': phone,
        'email': email,
        'address': address.toJson(),
        'business_type': businessType,
        'delivery_preference': deliveryPreference,
        if (panDocumentBase64 != null) 'pan_document': panDocumentBase64,
        if (gstDocumentBase64 != null) 'gst_document': gstDocumentBase64,
        if (cancelledChequeBase64 != null) 'cancelled_cheque': cancelledChequeBase64,
      };
}

class KycAddress {
  final String line1;
  final String? line2;
  final String city;
  final String state;
  final String pincode;

  const KycAddress({
    required this.line1,
    this.line2,
    required this.city,
    required this.state,
    required this.pincode,
  });

  Map<String, dynamic> toJson() => {
        'line1': line1,
        if (line2 != null && line2!.isNotEmpty) 'line2': line2,
        'city': city,
        'state': state,
        'pincode': pincode,
      };
}

/// Response from GET/POST retailer KYC (status and optional message).
class KycStatusResponse {
  final String status; // PENDING, APPROVED, REJECTED
  final String? message;
  final String? rejectionReason;

  const KycStatusResponse({
    required this.status,
    this.message,
    this.rejectionReason,
  });

  factory KycStatusResponse.fromJson(Map<String, dynamic> json) {
    return KycStatusResponse(
      status: json['status'] as String? ?? json['kyc_status'] as String? ?? 'PENDING',
      message: json['message'] as String?,
      rejectionReason: json['rejection_reason'] as String?,
    );
  }
}

/// Retailer KYC API (GET status, POST submit). Paths under /api/v1/retailer/kyc.
class RetailerKycService {
  final api.ApiClient _apiClient;

  RetailerKycService(this._apiClient);

  /// Set Bearer token for authenticated requests (call before getKycStatus/submitKyc).
  void setAccessToken(String? token) => _apiClient.setAccessToken(token);

  static const String _prefix = '/api/v1/retailer/kyc';

  /// Get current KYC status for the authenticated retailer.
  Future<api.ApiResponse<KycStatusResponse>> getKycStatus() async {
    return await _apiClient.get(
      _prefix,
      fromJson: (json) => KycStatusResponse.fromJson(json as Map<String, dynamic>),
    );
  }

  /// Submit KYC application (business details + documents).
  Future<api.ApiResponse<KycStatusResponse>> submitKyc(KycSubmitRequest request) async {
    return await _apiClient.post(
      _prefix,
      body: request.toJson(),
      fromJson: (json) => KycStatusResponse.fromJson(json as Map<String, dynamic>),
    );
  }
}
