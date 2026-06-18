// lib/models/user.dart

class User {
  final String userId;
  final String email;
  final String name;
  final String? token;

  const User({
    required this.userId,
    required this.email,
    required this.name,
    this.token,
  });

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      userId: json['user_id'] ?? '',
      email: json['email'] ?? '',
      name: json['name'] ?? '',
      token: json['token'],
    );
  }

  Map<String, dynamic> toJson() => {
        'user_id': userId,
        'email': email,
        'name': name,
        if (token != null) 'token': token,
      };

  User copyWith({String? token}) => User(
        userId: userId,
        email: email,
        name: name,
        token: token ?? this.token,
      );
}
