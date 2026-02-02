import 'package:json_annotation/json_annotation.dart';

@JsonEnum()
enum PaymentMethod {
  @JsonValue('UPI')
  upi,
  @JsonValue('CARD')
  card,
  @JsonValue('WALLET')
  wallet,
  @JsonValue('COD')
  cod,
  @JsonValue('BNPL')
  bnpl,
}
