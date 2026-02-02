import 'package:json_annotation/json_annotation.dart';

@JsonEnum()
enum OrderStatus {
  @JsonValue('PLACED')
  placed,
  @JsonValue('CONFIRMED')
  confirmed,
  @JsonValue('PACKED')
  packed,
  @JsonValue('OUT_FOR_DELIVERY')
  outForDelivery,
  @JsonValue('DELIVERED')
  delivered,
  @JsonValue('CANCELLED')
  cancelled,
}

@JsonEnum()
enum PaymentStatus {
  @JsonValue('PENDING')
  pending,
  @JsonValue('PAID')
  paid,
  @JsonValue('FAILED')
  failed,
  @JsonValue('REFUNDED')
  refunded,
}
