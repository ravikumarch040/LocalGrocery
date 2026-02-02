import 'package:shared_preferences/shared_preferences.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

/// Local storage service for managing app data
class StorageService {
  static final StorageService _instance = StorageService._internal();
  factory StorageService() => _instance;
  StorageService._internal();

  SharedPreferences? _prefs;
  final _secureStorage = const FlutterSecureStorage();

  /// Initialize storage
  Future<void> init() async {
    _prefs = await SharedPreferences.getInstance();
  }

  /// Save string value
  Future<bool> setString(String key, String value) async {
    return await _prefs?.setString(key, value) ?? false;
  }

  /// Get string value
  String? getString(String key) {
    return _prefs?.getString(key);
  }

  /// Save boolean value
  Future<bool> setBool(String key, bool value) async {
    return await _prefs?.setBool(key, value) ?? false;
  }

  /// Get boolean value
  bool? getBool(String key) {
    return _prefs?.getBool(key);
  }

  /// Save int value
  Future<bool> setInt(String key, int value) async {
    return await _prefs?.setInt(key, value) ?? false;
  }

  /// Get int value
  int? getInt(String key) {
    return _prefs?.getInt(key);
  }

  /// Remove value
  Future<bool> remove(String key) async {
    return await _prefs?.remove(key) ?? false;
  }

  /// Clear all data
  Future<bool> clear() async {
    return await _prefs?.clear() ?? false;
  }

  /// Save secure string (for tokens, passwords)
  Future<void> setSecureString(String key, String value) async {
    await _secureStorage.write(key: key, value: value);
  }

  /// Get secure string
  Future<String?> getSecureString(String key) async {
    return await _secureStorage.read(key: key);
  }

  /// Remove secure value
  Future<void> removeSecure(String key) async {
    await _secureStorage.delete(key: key);
  }

  /// Clear all secure storage
  Future<void> clearSecure() async {
    await _secureStorage.deleteAll();
  }
}
