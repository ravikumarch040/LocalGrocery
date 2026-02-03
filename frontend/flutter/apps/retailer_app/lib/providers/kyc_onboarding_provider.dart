import 'dart:convert';
import 'dart:io';
import 'package:api_client/api_client.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'api_providers.dart';
import 'auth_provider.dart';

/// Form state for the multi-step KYC onboarding flow.
class KycOnboardingState {
  final int currentStep;
  final String businessName;
  final String ownerName;
  final String phone;
  final String email;
  final String addressLine1;
  final String addressLine2;
  final String city;
  final String state;
  final String pincode;
  final String businessType;
  final String deliveryPreference;
  final String? panImagePath;
  final String? gstImagePath;
  final String? cancelledChequePath;
  final bool isSubmitting;
  final String? submitError;

  const KycOnboardingState({
    this.currentStep = 0,
    this.businessName = '',
    this.ownerName = '',
    this.phone = '',
    this.email = '',
    this.addressLine1 = '',
    this.addressLine2 = '',
    this.city = '',
    this.state = '',
    this.pincode = '',
    this.businessType = 'Kirana',
    this.deliveryPreference = 'Platform',
    this.panImagePath,
    this.gstImagePath,
    this.cancelledChequePath,
    this.isSubmitting = false,
    this.submitError,
  });

  KycOnboardingState copyWith({
    int? currentStep,
    String? businessName,
    String? ownerName,
    String? phone,
    String? email,
    String? addressLine1,
    String? addressLine2,
    String? city,
    String? state,
    String? pincode,
    String? businessType,
    String? deliveryPreference,
    String? panImagePath,
    String? gstImagePath,
    String? cancelledChequePath,
    bool? isSubmitting,
    String? submitError,
  }) {
    return KycOnboardingState(
      currentStep: currentStep ?? this.currentStep,
      businessName: businessName ?? this.businessName,
      ownerName: ownerName ?? this.ownerName,
      phone: phone ?? this.phone,
      email: email ?? this.email,
      addressLine1: addressLine1 ?? this.addressLine1,
      addressLine2: addressLine2 ?? this.addressLine2,
      city: city ?? this.city,
      state: state ?? this.state,
      pincode: pincode ?? this.pincode,
      businessType: businessType ?? this.businessType,
      deliveryPreference: deliveryPreference ?? this.deliveryPreference,
      panImagePath: panImagePath ?? this.panImagePath,
      gstImagePath: gstImagePath ?? this.gstImagePath,
      cancelledChequePath: cancelledChequePath ?? this.cancelledChequePath,
      isSubmitting: isSubmitting ?? this.isSubmitting,
      submitError: submitError ?? this.submitError,
    );
  }

  static const List<String> businessTypes = ['Kirana', 'Supermarket', 'Pharmacy', 'Other'];
  static const List<String> deliveryPreferences = ['Self', 'Platform', 'Third-party'];
}

class KycOnboardingNotifier extends StateNotifier<KycOnboardingState> {
  KycOnboardingNotifier(this._kycService, this._getToken) : super(const KycOnboardingState());

  final RetailerKycService _kycService;
  final Future<String?> Function() _getToken;

  void setStep(int step) {
    state = state.copyWith(currentStep: step, submitError: null);
  }

  void nextStep() {
    if (state.currentStep < 3) state = state.copyWith(currentStep: state.currentStep + 1, submitError: null);
  }

  void previousStep() {
    if (state.currentStep > 0) state = state.copyWith(currentStep: state.currentStep - 1, submitError: null);
  }

  void updateBasicDetails({
    String? businessName,
    String? ownerName,
    String? phone,
    String? email,
    String? addressLine1,
    String? addressLine2,
    String? city,
    String? addressState,
    String? pincode,
  }) {
    state = state.copyWith(
      businessName: businessName,
      ownerName: ownerName,
      phone: phone,
      email: email,
      addressLine1: addressLine1,
      addressLine2: addressLine2,
      city: city,
      addressState: addressState,
      pincode: pincode,
    );
  }

  void updateBusinessType({String? businessType, String? deliveryPreference}) {
    state = state.copyWith(businessType: businessType, deliveryPreference: deliveryPreference);
  }

  void setPanImage(String? path) => state = state.copyWith(panImagePath: path);
  void setGstImage(String? path) => state = state.copyWith(gstImagePath: path);
  void setCancelledChequeImage(String? path) => state = state.copyWith(cancelledChequePath: path);

  static Future<String?> _fileToBase64(String path) async {
    try {
      final file = File(path);
      if (!await file.exists()) return null;
      final bytes = await file.readAsBytes();
      return base64Encode(bytes);
    } catch (_) {
      return null;
    }
  }

  Future<bool> submit() async {
    state = state.copyWith(isSubmitting: true, submitError: null);
    try {
      final token = await _getToken();
      _kycService.setAccessToken(token);

      final panBase64 = state.panImagePath != null ? await _fileToBase64(state.panImagePath!) : null;
      final gstBase64 = state.gstImagePath != null ? await _fileToBase64(state.gstImagePath!) : null;
      final chequeBase64 = state.cancelledChequePath != null ? await _fileToBase64(state.cancelledChequePath!) : null;

      final request = KycSubmitRequest(
        businessName: state.businessName.trim(),
        ownerName: state.ownerName.trim(),
        phone: state.phone.trim(),
        email: state.email.trim(),
        address: KycAddress(
          line1: state.addressLine1.trim(),
          line2: state.addressLine2.trim().isEmpty ? null : state.addressLine2.trim(),
          city: state.city.trim(),
          state: state.state.trim(),
          pincode: state.pincode.trim(),
        ),
        businessType: state.businessType,
        deliveryPreference: state.deliveryPreference,
        panDocumentBase64: panBase64,
        gstDocumentBase64: gstBase64,
        cancelledChequeBase64: chequeBase64,
      );

      final res = await _kycService.submitKyc(request);
      state = state.copyWith(isSubmitting: false);
      if (res.success) {
        return true;
      }
      state = state.copyWith(submitError: res.message ?? 'Submission failed');
      return false;
    } catch (e) {
      state = state.copyWith(isSubmitting: false, submitError: e.toString());
      return false;
    }
  }

  void clearError() => state = state.copyWith(submitError: null);
  void reset() => state = const KycOnboardingState();
}

final kycOnboardingProvider = StateNotifierProvider<KycOnboardingNotifier, KycOnboardingState>((ref) {
  final kycService = ref.watch(retailerKycServiceProvider);
  final getToken = () => ref.read(authProvider.notifier).getAccessToken();
  return KycOnboardingNotifier(kycService, getToken);
});
