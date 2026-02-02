import 'package:json_annotation/json_annotation.dart';
import 'package:equatable/equatable.dart';

part 'otp_request.g.dart';

@JsonSerializable()
class SendOtpRequest extends Equatable {
  final String phone;

  const SendOtpRequest({required this.phone});

  factory SendOtpRequest.fromJson(Map<String, dynamic> json) => _$SendOtpRequestFromJson(json);
  Map<String, dynamic> toJson() => _$SendOtpRequestToJson(this);

  @override
  List<Object?> get props => [phone];
}

@JsonSerializable()
class VerifyOtpRequest extends Equatable {
  final String phone;
  final String otp;

  const VerifyOtpRequest({
    required this.phone,
    required this.otp,
  });

  factory VerifyOtpRequest.fromJson(Map<String, dynamic> json) => _$VerifyOtpRequestFromJson(json);
  Map<String, dynamic> toJson() => _$VerifyOtpRequestToJson(this);

  @override
  List<Object?> get props => [phone, otp];
}
