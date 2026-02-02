import 'package:json_annotation/json_annotation.dart';
import 'package:equatable/equatable.dart';

part 'api_response.g.dart';

@JsonSerializable(genericArgumentFactories: true)
class ApiResponse<T> extends Equatable {
  final bool success;
  final String message;
  final T? data;
  final ErrorDetails? error;

  const ApiResponse({
    required this.success,
    required this.message,
    this.data,
    this.error,
  });

  factory ApiResponse.fromJson(
    Map<String, dynamic> json,
    T Function(Object? json) fromJsonT,
  ) =>
      _$ApiResponseFromJson(json, fromJsonT);

  Map<String, dynamic> toJson(Object? Function(T value) toJsonT) =>
      _$ApiResponseToJson(this, toJsonT);

  @override
  List<Object?> get props => [success, message, data, error];
}

@JsonSerializable()
class ErrorDetails extends Equatable {
  final String code;
  final int httpStatus;
  final Map<String, dynamic>? details;

  const ErrorDetails({
    required this.code,
    required this.httpStatus,
    this.details,
  });

  factory ErrorDetails.fromJson(Map<String, dynamic> json) => _$ErrorDetailsFromJson(json);
  Map<String, dynamic> toJson() => _$ErrorDetailsToJson(this);

  @override
  List<Object?> get props => [code, httpStatus, details];
}
