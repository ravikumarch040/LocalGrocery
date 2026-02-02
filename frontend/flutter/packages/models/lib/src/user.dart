/// User model
class User {
  final String id;
  final String phoneNumber;
  final String? name;
  final String? email;
  final String role; // CUSTOMER, RETAILER, DELIVERY_PARTNER, ADMIN
  final DateTime createdAt;
  final DateTime? updatedAt;

  User({
    required this.id,
    required this.phoneNumber,
    this.name,
    this.email,
    required this.role,
    required this.createdAt,
    this.updatedAt,
  });

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'] as String,
      phoneNumber: json['phone_number'] as String,
      name: json['name'] as String?,
      email: json['email'] as String?,
      role: json['role'] as String,
      createdAt: DateTime.parse(json['created_at'] as String),
      updatedAt: json['updated_at'] != null
          ? DateTime.parse(json['updated_at'] as String)
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'phone_number': phoneNumber,
      'name': name,
      'email': email,
      'role': role,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt?.toIso8601String(),
    };
  }

  User copyWith({
    String? name,
    String? email,
  }) {
    return User(
      id: id,
      phoneNumber: phoneNumber,
      name: name ?? this.name,
      email: email ?? this.email,
      role: role,
      createdAt: createdAt,
      updatedAt: DateTime.now(),
    );
  }

  bool get isCustomer => role == 'CUSTOMER';
  bool get isRetailer => role == 'RETAILER';
  bool get isDeliveryPartner => role == 'DELIVERY_PARTNER';
  bool get isAdmin => role == 'ADMIN';
}
