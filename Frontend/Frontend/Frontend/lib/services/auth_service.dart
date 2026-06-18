// lib/services/auth_service.dart

import 'package:shared_preferences/shared_preferences.dart';
import '../config/api_config.dart';
import '../models/user.dart';
import 'api_service.dart';

class AuthService {
  final ApiService _api;

  static const _keyUserId = 'user_id';
  static const _keyEmail = 'email';
  static const _keyName = 'name';

  AuthService(this._api);

  // Backend only has /users/create with name + email (no password/login yet)
  Future<User> register({
    required String name,
    required String email,
    required String password, // kept for UI compatibility, not sent
  }) async {
    final data = await _api.post(ApiConfig.register, data: {
      'name': name,
      'email': email,
    });

    final user = User.fromJson(data['user'] ?? data);
    await _saveUser(user);
    return user;
  }

  // No login endpoint exists yet — match by email from stored user
  Future<User> login({
    required String email,
    required String password,
  }) async {
    // Check if we have a stored user with this email
    final stored = await getStoredUser();
    if (stored != null && stored.email == email) {
      return stored;
    }
    throw 'No account found for $email. Please sign up first.';
  }

  Future<User?> getStoredUser() async {
    final prefs = await SharedPreferences.getInstance();
    final userId = prefs.getString(_keyUserId);
    if (userId == null) return null;

    return User(
      userId: userId,
      email: prefs.getString(_keyEmail) ?? '',
      name: prefs.getString(_keyName) ?? '',
    );
  }

  Future<void> logout() async {
    _api.clearAuthToken();
    final prefs = await SharedPreferences.getInstance();
    await prefs.clear();
  }

  Future<void> _saveUser(User user) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_keyUserId, user.userId);
    await prefs.setString(_keyEmail, user.email);
    await prefs.setString(_keyName, user.name);
  }
}
